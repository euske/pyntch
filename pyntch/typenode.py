#!/usr/bin/env python
##
##  typenode.py
##

import sys
try:
  from xml.etree.cElementTree import Element
except ImportError:
  from xml.etree.ElementTree import Element

class NodeError(Exception): pass
class NodeTypeError(NodeError): pass
class NodeAttrError(NodeError): pass
class NodeAssignError(NodeError): pass


##  TypeNode
##
##  A TypeNode object represents a place where a potential
##  data could be stored or passed in the course of execution of
##  the whole program. The data once stored in a node can be propagated to
##  other nodes via one or multiple outbound links.
##
class TypeNode(object):

  verbose = 0
  debug = 0
  nodes = 0

  procs = set()

  @classmethod
  def inc(klass):
    klass.nodes += 1
    return

  @classmethod
  def schedule(klass, proc, obj):
    klass.procs.add((proc, obj))
    return
  
  @classmethod
  def run(klass):
    while klass.procs:
      if klass.verbose:
        print >>sys.stderr, 'processing: %d nodes (%d left)' % (klass.nodes, len(klass.procs))
      (procs, klass.procs) = (klass.procs, set())
      for (proc,obj) in procs:
        proc(obj)
    return
  
  def __init__(self, types):
    self.types = set(types)
    self.sendto = []
    TypeNode.inc()
    return

  def __iter__(self):
    return iter(list(self.types))

  # connect(receiver): connects this node to
  # another node and designates that any data stored at
  # this node be propagated to the other node(s).
  # The receiver parameter is either CompoundTypeNode object or
  # a function object that receives a value every time it changed.
  def connect(self, receiver):
    assert callable(receiver)
    if self.debug:
      print >>sys.stderr, 'connect: %r -> %r' % (self, receiver)
    if receiver in self.sendto: return False
    self.sendto.append(receiver)
    self.schedule(receiver, self)
    return

  def get_attr(self, frame, anchor, name, write=False):
    raise NodeAttrError(name)
  def get_element(self, frame, anchor, sub, write=False):
    raise NodeTypeError('not subscriptable')
  def get_slice(self, frame, anchor, subs, write=False):
    raise NodeTypeError('not subscriptable')
  def get_iter(self, frame, anchor):
    raise NodeTypeError('not iterable')
  def get_reversed(self, frame, anchor):
    raise NodeTypeError('not reverse-iterable')
  def get_length(self, frame, anchor):
    raise NodeTypeError('no len()')
  def call(self, frame, anchor, args, kwargs):
    raise NodeTypeError('not callable')

  def is_type(self, *_):
    return False
  
  def desctxt(self, _):
    raise NotImplementedError, self.__class__
  def descxml(self, _):
    raise NotImplementedError, self.__class__


##  SimpleTypeNode
##
##  A SimpleTypeNode holds a particular type of value.
##  This type of nodes can be a leaf in a typeflow graph
##  and is not altered after creation.
##
class SimpleTypeNode(TypeNode):

  def __init__(self, typeobj):
    assert isinstance(typeobj, TypeNode), typeobj
    self.typeobj = typeobj
    TypeNode.__init__(self, [self])
    return

  def __repr__(self):
    return '<%s>' % self.get_type().typename()

  def desctxt(self, done):
    done[self] = len(done)
    return repr(self)
  
  def descxml(self, done):
    done[self] = len(done)
    return Element(self.get_type().typename())
  
  def get_type(self):
    return self.typeobj


##  CompoundTypeNode
##
##  A CompoundTypeNode holds a multiple types of values that
##  can be potentially stored. This type of nodes can have
##  both inbound and outbound links and the data stored in the node
##  can be further propagated to other nodes.
##
class CompoundTypeNode(TypeNode):

  def __init__(self, nodes=None):
    TypeNode.__init__(self, [])
    if nodes:
      for obj in nodes:
        obj.connect(self.recv)
    return

  def __repr__(self):
    return '<CompoundTypeNode: %d>' % len(self.types)

  def recv(self, src):
    for obj in src:
      self.update_type(obj)
    return
  
  def update_type(self, obj):
    assert not isinstance(obj, CompoundTypeNode)
    if obj in self.types: return
    #print 'add', id(self), id(obj), obj
    self.types.add(obj)
    for receiver in self.sendto:
      self.schedule(receiver, self)
    return True

  def desctxt(self, done):
    if self in done:
      return '...'
    elif self.types:
      done[self] = len(done)
      return '|'.join( sorted(set( obj.desctxt(done) for obj in self )) )
    else:
      return '?'
    
  def descxml(self, done):
    if self in done:
      e = Element('ref', id=str(done[self]))
    else:
      done[self] = len(done)
      e = Element('compound', id=str(done[self]))
      for obj in self:
        e.append(obj.descxml(done))
    return e
                                  

##  UndefinedTypeNode
##
##  An UndefinedTypeNode is a special TypeNode object that
##  represents an undefined value. This node can be used as
##  a value in undefined variables or undefined attribues,
##  or a return value from illegal function calls. All the operation
##  on this node always returns itself (i.e. any operation on
##  undefined value is always undefined.)
##
class UndefinedTypeNode(TypeNode):
  
  OBJECT = None
  @classmethod
  def get_object(klass):
    if not klass.OBJECT:
      klass.OBJECT = klass()
    return klass.OBJECT

  def __init__(self, name=None):
    TypeNode.__init__(self, [])
    return
  
  def __repr__(self):
    return '(undef)'
  
  def desctxt(self, _):
    return '(undef)'
  def descxml(self, _):
    return Element('undef')

  def recv(self, src):
    return
  def get_attr(self, frame, anchor, name, write=False):
    return self
  def get_element(self, frame, anchor, sub, write=False):
    return self
  def get_slice(self, frame, anchor, subs, write=False):
    return self
  def get_iter(self, frame, anchor):
    return self
  def get_reversed(self, frame, anchor):
    return self
  def get_length(self, frame, anchor):
    return self
  def call(self, frame, anchor, args, kwargs):
    return self


##  BuiltinObject
##
class BuiltinObject(SimpleTypeNode):

  def get_attr(self, frame, anchor, name, write=False):
    from pyntch.basic_types import StrType
    if name == '__class__':
      if write: raise NodeAssignError(name)
      return self.get_type()
    elif name == '__doc__':
      return StrType.get_object()
    return self.get_type().get_attr(frame, anchor, name, write=write)
  
  def is_type(self, *typeobjs):
    for typeobj in typeobjs:
      if self.typeobj is typeobj or issubclass(self.typeobj.__class__, typeobj.__class__): return True
    return False


##  BuiltinType
##
class BuiltinType(BuiltinObject):

  TYPE_NAME = None # must be defined by subclass
  TYPEOBJS = {}

  def __init__(self):
    self.initialize(self)
    SimpleTypeNode.__init__(self, self)
    return

  def __repr__(self):
    return '<type %s>' % self.typename()
  
  @classmethod
  def get_type(klass):
    from pyntch.basic_types import TypeType
    return TypeType.get_typeobj()
  
  @classmethod
  def is_type(klass, *typeobjs):
    from pyntch.basic_types import TypeType
    return TypeType.get_typeobj() in typeobjs

  # typename()
  # returns the name of the Python type of this object.
  @classmethod
  def typename(klass):
    return klass.TYPE_NAME

  # get_typeobj()
  @classmethod
  def get_typeobj(klass):
    if klass not in klass.TYPEOBJS:
      klass()
    return klass.TYPEOBJS[klass]

  @classmethod
  def initialize(klass, obj):
    klass.TYPEOBJS[klass] = obj
    return

  # default methods
  class InitMethod(BuiltinObject):
    def call(self, frame, anchor, args, kwargs):
      from pyntch.basic_types import NoneType
      return NoneType.get_object()

  def get_attr(self, frame, anchor, name, write=False):
    raise NodeAttrError(name)


##  BuiltinCallable
##
##  A helper class to augment builtin objects (mostly type objects)
##  for behaving like a function.
##
class BuiltinCallable(object):

  def __init__(self, name, args=None, optargs=None, expts=None):
    args = (args or [])
    optargs = (optargs or [])
    self.name = name
    self.minargs = len(args)
    self.args = args+optargs
    self.expts = (expts or [])
    return
  
  def call(self, frame, anchor, args, kwargs):
    from pyntch.config import ErrorConfig
    if len(args) < self.minargs:
      frame.raise_expt(ErrorConfig.InvalidNumOfArgs(self.minargs, len(args)))
      return UndefinedTypeNode.get_object()
    if len(self.args) < len(args):
      frame.raise_expt(ErrorConfig.InvalidNumOfArgs(len(self.args), len(args)))
      return UndefinedTypeNode.get_object()
    return self.process_args(frame, anchor, args, kwargs)

  def process_args(self, frame, anchor, args, kwargs):
    raise NotImplementedError, self.__class__


##  BuiltinConstCallable
##
class BuiltinConstCallable(BuiltinCallable):
  
  def __init__(self, name, retobj, args=None, optargs=None, expts=None):
    self.retobj = retobj
    BuiltinCallable.__init__(self, name, args=args, optargs=optargs, expts=expts)
    return

  def process_args(self, frame, anchor, args, kwargs):
    from pyntch.config import ErrorConfig
    if kwargs:
      frame.raise_expt(ErrorConfig.NoKeywordArgs())
    for (i,arg1) in enumerate(args):
      assert isinstance(arg1, TypeNode)
      self.accept_arg(frame, anchor, i, arg1)
    for expt in self.expts:
      frame.raise_expt(expt)
    return self.retobj

  def accept_arg(self, frame, anchor, i, arg1):
    s = 'arg %d' % i
    spec = self.args[i]
    if isinstance(spec, list):
      if spec == [TypeChecker.ANY]:
        checker = SequenceTypeChecker(frame, anchor, TypeChecker.ANY, s)
      else:
        checker = SequenceTypeChecker(frame, anchor, [ x.get_typeobj() for x in spec ], s)
    elif isinstance(spec, tuple):
      checker = TypeChecker(frame, [ x.get_typeobj() for x in spec ], s)
    elif spec == TypeChecker.ANY:
      checker = TypeChecker(frame, TypeChecker.ANY, s)
    else:
      checker = TypeChecker(frame, [spec.get_typeobj()], s)
    arg1.connect(checker.recv)
    return


##  BuiltinMethod
##
class BuiltinMethodType(BuiltinType):
  TYPE_NAME = 'builtin_method'


##  BuiltinMethod
##
class BuiltinMethod(BuiltinCallable, BuiltinObject):
  
  def __init__(self, name, args=None, optargs=None, expts=None):
    BuiltinObject.__init__(self, BuiltinMethodType.get_typeobj())
    BuiltinCallable.__init__(self, name, args=args, optargs=optargs, expts=expts)
    return

  def __repr__(self):
    return '<callable %s>' % self.name

##  BuiltinConstMethod
##
class BuiltinConstMethod(BuiltinConstCallable, BuiltinObject):

  def __init__(self, name, retobj, args=None, optargs=None, expts=None):
    BuiltinObject.__init__(self, BuiltinMethodType.get_typeobj())
    BuiltinConstCallable.__init__(self, name, retobj, args=args, optargs=optargs, expts=expts)
    return

  def __repr__(self):
    return '<callable %s>' % self.name


##  TypeChecker
##
class TypeChecker(CompoundTypeNode):

  ANY = 'any'
  nodes = None
  
  def __init__(self, parent_frame, types, blame):
    self.parent_frame = parent_frame
    self.blame = blame
    self.received = set()
    if types == self.ANY:
      self.validtypes = self.ANY
    else:
      self.validtypes = CompoundTypeNode(types)
    CompoundTypeNode.__init__(self)
    TypeChecker.nodes.append(self)
    return

  def __repr__(self):
    return ('<TypeChecker: %s: %s>' % 
            (','.join(map(repr, self.types)), self.validtypes))

  @classmethod
  def reset(klass):
    klass.nodes = []
    return
  
  @classmethod
  def check(klass):
    for node in klass.nodes:
      node.check_type()
    return

  def recv(self, src):
    for obj in src:
      self.received.add(obj)
    return

  def check_type(self):
    from pyntch.config import ErrorConfig
    from pyntch.basic_types import TypeType
    if self.validtypes == self.ANY: return
    for obj in self.received:
      for typeobj in self.validtypes:
        if typeobj.is_type(TypeType.get_typeobj()) and obj.is_type(typeobj):
          self.update_type(obj)
          break
      else:
        s = '|'.join( typeobj.typename() for typeobj in self.validtypes
                      if typeobj.is_type(TypeType.get_typeobj()) )
        self.parent_frame.raise_expt(ErrorConfig.TypeCheckerError(self.blame, obj, s))
    return


##  SequenceTypeChecker
##
class SequenceTypeChecker(CompoundTypeNode):
  
  def __init__(self, parent_frame, anchor, types, blame):
    CompoundTypeNode.__init__(self)
    self.parent_frame = parent_frame
    self.anchor = anchor
    self.received = set()
    self.elemchecker = TypeChecker(parent_frame, types, blame+' element')
    return
  
  def __repr__(self):
    return ('<SequenceTypeChecker: %s: %s>' % 
            (','.join(map(repr, self.types)), self.elemchecker))

  def recv(self, src):
    from pyntch.expression import IterElement
    for obj in src:
      if obj in self.received: continue
      self.received.add(obj)
      IterElement(self.parent_frame, self.anchor, obj).connect(self.elemchecker.recv)
    return


##  KeyValueTypeChecker
##
class KeyValueTypeChecker(CompoundTypeNode):
  
  def __init__(self, parent_frame, keys, values, blame):
    CompoundTypeNode.__init__(self)
    self.parent_frame = parent_frame
    self.received = set()
    self.keychecker = TypeChecker(parent_frame, keys, blame+' dict key')
    self.valuechecker = TypeChecker(parent_frame, values, blame+' dict value')
    return
    
  def __repr__(self):
    return ('<KeyValueTypeChecker: %s: %s:%s>' % 
            (','.join(map(repr, self.types)), self.keychecker, self.valuechecker))

  def recv(self, src):
    from pyntch.config import ErrorConfig
    from pyntch.aggregate_types import DictObject
    for obj in src:
      if obj in self.received: continue
      self.received.add(obj)
      if isinstance(obj, DictObject):
        obj.key.connect(self.keychecker.recv)
        obj.value.connect(self.valuechecker.recv)
      else:
        self.parent_frame.raise_expt(ErrorConfig.TypeCheckerError(self.blame, obj, 'dict'))
    return
