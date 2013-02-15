#!/usr/bin/env python

from pyntch.typenode import CompoundTypeNode, UndefinedTypeNode, \
     NodeTypeError, NodeAttrError, NodeAssignError, BuiltinType, BuiltinObject, \
     TypeChecker, Element
from pyntch.namespace import Namespace
from pyntch.module import TreeReporter
from pyntch.frame import ExecutionFrame


##  MethodType
##
class MethodType(BuiltinType):

  TYPE_NAME = 'method'

  def __init__(self, klass, func):
    self.klass = klass
    self.func = func
    BuiltinType.__init__(self)
    return

  def __repr__(self):
    return '<method %r>' % self.func
  
  def descxml(self, done):
    done[self] = len(done)
    return Element('method', name=self.func.get_name())
  
  def get_type(self):
    return self

  def call(self, frame, anchor, args, kwargs):
    from pyntch.config import ErrorConfig
    if len(args) == 0:
      frame.raise_expt(ErrorConfig.InvalidNumOfArgs(1, len(args)))
      return UndefinedTypeNode.get_object()
    arg0checker = TypeChecker(frame, [self.klass], 'arg0')
    args[0].connect(arg0checker.recv)
    return self.func.call(frame, anchor, args, kwargs)


##  BoundMethodType
##
class BoundMethodType(BuiltinType):

  TYPE_NAME = 'boundmethod'

  def __init__(self, arg0, func):
    self.arg0 = arg0
    self.func = func
    BuiltinType.__init__(self)
    return

  def __repr__(self):
    return '<boundmethod %r(arg0=%r)>' % (self.func, self.arg0)
  
  def descxml(self, done):
    done[self] = len(done)
    return Element('boundmethod', name=self.func.get_name())
  
  def get_type(self):
    return self

  def call(self, frame, anchor, args, kwargs):
    return self.func.call(frame, anchor, (self.arg0,)+tuple(args), kwargs)


##  ClassType
##  Built-in class or class defined in Python code.
##
class ClassType(BuiltinType, TreeReporter):

  TYPE_NAME = 'class'
  
  ##  ClassAttr
  ##
  class ClassAttr(CompoundTypeNode):

    def __init__(self, frame, anchor, name, klass, klasses=None):
      self.frame = frame
      self.anchor = anchor
      self.name = name
      self.klass = klass
      self.processed = set()
      CompoundTypeNode.__init__(self)
      if klasses:
        klasses.connect(self.recv_klass)
      return

    def __repr__(self):
      return '%r.%s' % (self.klass, self.name)

    def recv_klass(self, src):
      for klass in src:
        try:
          klass.get_attr(self.frame, self.anchor, self.name).connect(self.recv)
        except NodeAttrError:
          pass
      return

    def recv(self, src):
      from pyntch.function import FuncType
      from pyntch.basic_types import StaticMethodObject, ClassMethodObject
      for obj in src:
        if obj in self.processed: continue
        self.processed.add(obj)
        if isinstance(obj, StaticMethodObject):
          obj = obj.get_object()
        elif isinstance(obj, ClassMethodObject):
          obj = self.klass.bind_func(obj.get_object())
        elif isinstance(obj, FuncType):
          obj = MethodType(self.klass, obj)
        self.update_type(obj)
      return
    
  def __init__(self, name, bases):
    self.name = name
    self.bases = bases
    self.attrs = {}
    self.boundmethods = {}
    self.frames = set()
    BuiltinType.__init__(self)
    self.klasses = CompoundTypeNode(bases+[self])
    self.instance = InstanceObject(self)
    return

  def __repr__(self):
    return ('<class %s>' % self.get_name())

  def get_name(self):
    return self.name
  
  def descxml(self, done):
    done[self] = len(done)
    return Element('class', name=self.get_name())
  
  def typename(self):
    return self.name
  
  def is_subclass(self, klassobj):
    if self is klassobj: return True
    for klass in self.klasses:
      if klass is not self and isinstance(klass, ClassType):
        if klass.is_subclass(klassobj): return True
    return False

  def get_attr(self, frame, anchor, name, write=False):
    if name == '__class__':
      if write: raise NodeAssignError(name)
      return self.get_type()
    elif name not in self.attrs:
      attr = self.ClassAttr(frame, anchor, name, self, self.klasses)
      self.attrs[name] = attr
    else:
      attr = self.attrs[name]
    return attr

  def bind_func(self, func):
    if func not in self.boundmethods:
      method = BoundMethodType(self, func)
      self.boundmethods[func] = method
    else:
      method = self.boundmethods[func]
    return method

  def call(self, frame, anchor, args, kwargs):
    from pyntch.expression import OptMethodCall
    assert isinstance(frame, ExecutionFrame)
    self.frames.add(frame)
    OptMethodCall(frame, anchor, self.instance, '__init__', args, kwargs)
    return self.instance


##  PythonClassType
##  A class type that is associated with an actual Python code.
##
class PythonClassType(ClassType, TreeReporter):
  
  def __init__(self, parent_reporter, parent_frame, parent_space, anchor, name, bases, evals, tree):
    from pyntch.syntax import build_stmt
    self.anchor = anchor
    self.loc = (tree._module, tree.lineno)
    self.space = Namespace(parent_space, name)
    TreeReporter.__init__(self, parent_reporter)
    ClassType.__init__(self, name, bases)
    if tree.code:
      self.space.register_names(tree.code)
      build_stmt(self, parent_frame, self.space, tree.code, evals, parent_space=parent_space)
    for (name,var) in self.space:
      # Do not consider the values of attributes inherited from the base class
      # if they are explicitly overriden.
      attr = self.ClassAttr(parent_frame, anchor, name, self)
      var.connect(attr.recv)
      self.attrs[name] = attr
    return

  def get_name(self):
    return self.space.get_name()
  
  def showtxt(self, out):
    (module,lineno) = self.loc
    out.write('### %s(%s)' % (module.get_name(), lineno))
    for frame in self.frames:
      (module,lineno) = frame.getloc()
      out.write('# instantiated at %s(%d)' % (module.get_name(), lineno))
    if self.bases:
      out.write('class %s(%s):' % (self.name,
                                   ', '.join( base.typename() for base in self.klasses if base is not self )))
    else:
      out.write('class %s:' % self.name)
    out.indent(+1)
    blocks = set( child.name for child in self.children )
    for (name, attr) in self.attrs.iteritems():
      if name in blocks or not attr.types: continue
      out.write_value('class.'+name, attr)
    for (name, attr) in self.instance.attrs.iteritems():
      if name in blocks or not attr.types: continue
      out.write_value('instance.'+name, attr)
    for child in self.children:
      child.showtxt(out)
    out.indent(-1)
    out.write('')
    return

  def showxml(self, out):
    (module,lineno) = self.loc
    out.start_xmltag('class', name=self.name)
    for frame in self.frames:
      (module,lineno) = frame.getloc()
      out.show_xmltag('caller',
                      loc='%s:%s' % (module.get_name(), lineno))
    for base in self.klasses:
      if base is self: continue
      out.show_xmltag('base', name=base.typename())
    blocks = set( child.name for child in self.children )
    for (name, attr) in self.attrs.iteritems():
      if name in blocks or not attr.types: continue
      out.show_xmlvalue('classattr', attr, name=name)
    for (name, attr) in self.instance.attrs.iteritems():
      if name in blocks or not attr.types: continue
      out.show_xmlvalue('instanceattr', attr, name=name)
    for child in self.children:
      child.showxml(out)
    out.end_xmltag('class')
    return


##  InstanceType
##
class InstanceObject(BuiltinObject):

  TYPE_NAME = 'instance'

  ##  InstanceAttr
  ##
  class InstanceAttr(CompoundTypeNode):

    def __init__(self, frame, anchor, name, klass, instance):
      self.frame = frame
      self.anchor = anchor
      self.name = name
      self.klass = klass
      self.instance = instance
      self.processed = set()
      CompoundTypeNode.__init__(self)
      klass.connect(self.recv_klass)
      return

    def __repr__(self):
      return '%r.%s' % (self.instance, self.name)
      
    def recv_klass(self, src):
      for klass in src:
        try:
          klass.get_attr(self.frame, self.anchor, self.name).connect(self.recv)
        except NodeAttrError:
          pass
        try:
          klass.instance.get_attr(self.frame, self.anchor, self.name).connect(self.recv)
        except NodeAttrError:
          pass
      return

    def recv(self, src):
      for obj in src:
        if obj in self.processed: continue
        self.processed.add(obj)
        if isinstance(obj, MethodType):
          obj = self.instance.bind_func(obj.func)
        self.update_type(obj)
      return
    
  #
  def __init__(self, klass):
    self.klass = klass
    self.attrs = {}
    self.boundmethods = {}
    BuiltinObject.__init__(self, klass)
    for name in klass.attrs.iterkeys():
      self.attrs[name] = self.InstanceAttr(None, None, name, self.klass, self)
    return
  
  def __repr__(self):
    return ('<instance %s>' % self.klass.get_name())
  
  def descxml(self, done):
    done[self] = len(done)
    return Element('instance', name=self.klass.get_name())
  
  def get_type(self):
    return self.klass

  def is_type(self, *typeobjs):
    for typeobj in typeobjs:
      if self.klass.is_subclass(typeobj): return True
    return False

  def get_attr(self, frame, anchor, name, write=False):
    if name == '__class__':
      if write: raise NodeAssignError(name)
      return self.get_type()
    elif name not in self.attrs:
      attr = self.InstanceAttr(frame, anchor, name, self.klass, self)
      self.attrs[name] = attr
    else:
      attr = self.attrs[name]
    return attr

  def get_iter(self, frame, anchor):
    from pyntch.expression import OptMethodCall
    assert isinstance(frame, ExecutionFrame)
    return OptMethodCall(frame, anchor, self, '__iter__')

  def get_reversed(self, frame, anchor):
    from pyntch.expression import OptMethodCall
    assert isinstance(frame, ExecutionFrame)
    return OptMethodCall(frame, anchor, self, '__reversed__')

  def get_length(self, frame, anchor):
    from pyntch.expression import OptMethodCall
    assert isinstance(frame, ExecutionFrame)
    return OptMethodCall(frame, anchor, self, '__len__')

  def get_element(self, frame, anchor, sub, write=False):
    from pyntch.expression import OptMethodCall
    if write:
      return OptMethodCall(frame, anchor, self, '__setelem__', sub)
    else:
      return OptMethodCall(frame, anchor, self, '__getelem__', sub)
    
  def get_slice(self, frame, anchor, subs, write=False):
    from pyntch.expression import OptMethodCall
    if write:
      return OptMethodCall(frame, anchor, self, '__setslice__', subs)
    else:
      return OptMethodCall(frame, anchor, self, '__getslice__', subs)

  def call(self, frame, anchor, args, kwargs):
    from pyntch.expression import OptMethodCall
    return OptMethodCall(frame, anchor, self, '__call__', args, kwargs)
  
  def bind_func(self, func):
    if func not in self.boundmethods:
      method = BoundMethodType(self, func)
      self.boundmethods[func] = method
    else:
      method = self.boundmethods[func]
    return method

class InstanceType(BuiltinType):
  TYPE_NAME = 'object'
