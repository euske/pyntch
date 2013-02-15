#!/usr/bin/env python
import sys
from pyntch.typenode import TypeNode, CompoundTypeNode, NodeTypeError, Element


##  TracebackObject
##
##  A TracebackObject is an exception object (or whatever is thrown)
##  associated with a specific execution frame.
##
class TracebackObject(TypeNode):

  def __init__(self, exptobj, frame):
    self.exptobj = exptobj
    self.frame = frame
    TypeNode.__init__(self, [self])
    return

  def __repr__(self):
    try:
      (module,lineno) = self.frame.getloc()
      return '%s at %s:%s' % (self.exptobj, module.get_name(), lineno)
    except TypeError:
      return '%s at ???' % self.exptobj


##  ExecutionFrame
##
##  An ExecutionFrame object represents a place where an exception
##  occurs.  Normally it's a body of every function and
##  method. Exceptions that are raised within this frame are
##  propagated to other ExecutionFrames which invoke the function.
##
class ExecutionFrame(CompoundTypeNode):

  expt_debug = 0

  def __init__(self, parent, tree):
    self.parent = parent
    self.raised = set()
    if tree:
      self.loc = (tree._module, tree.lineno)
    else:
      self.loc = None
    CompoundTypeNode.__init__(self)
    if parent:
      assert isinstance(parent, ExecutionFrame), parent
      if self.expt_debug:
        print >>sys.stderr, 'connect_expt: %r <- %r' % (parent, self)
      self.connect(parent.recv)
    return

  def __repr__(self):
    loc = self.getloc()
    if loc:
      (module,lineno) = loc
      return '<Frame at %s:%s>' % (module.get_name(), lineno)
    else:
      return '<Frame at ???>'

  def set_reraise(self):
    from pyntch.config import ErrorConfig
    self.raise_expt(ErrorConfig.RaiseOutsideTry())
    return

  def getloc(self):
    loc = None
    while self:
      loc = self.loc
      if loc: break
      self = self.parent
    return loc
  
  def raise_expt(self, expt):
    if not expt: return
    assert not isinstance(expt, CompoundTypeNode)
    if expt in self.raised: return
    self.raised.add(expt)
    if self.expt_debug:
      print >>sys.stderr, 'raise_expt: %r <- %r' % (self, expt)
    TracebackObject(expt, self).connect(self.recv)
    return

  def showtxt(self, out):
    from pyntch.config import ErrorConfig
    expts_here = []
    expts_there = []
    for expt in self:
      frame = expt.frame
      while frame:
        if frame == self:
          expts_here.append(expt)
          break
        frame = frame.parent
      else:
        expts_there.append(expt)
    for expt in sorted(expts_here, key=lambda expt:expt.frame.getloc()):
      out.write('raises %s' % expt)
    if ErrorConfig.show_all_exceptions:
      for expt in sorted(expts_there, key=lambda expt:expt.frame.getloc()):
        out.write('[raises %s]' % expt)
    return

  def showxml(self, out):
    from pyntch.config import ErrorConfig
    expts_here = []
    expts_there = []
    for expt in self:
      frame = expt.frame
      while frame:
        if frame == self:
          expts_here.append(expt)
          break
        frame = frame.parent
      else:
        expts_there.append(expt)
    for expt in sorted(expts_here, key=lambda expt:expt.frame.getloc()):
      (module, lineno) = expt.frame.getloc()
      obj = expt.exptobj
      out.show_xmltag('raise', type=obj.get_type().typename(), msg=str(obj),
                      loc='%s:%s' % (module.get_name(), lineno))
    if ErrorConfig.show_all_exceptions:
      for expt in sorted(expts_there, key=lambda expt:expt.frame.getloc()):
        obj = expt.exptobj
        out.show_xmltag('iraise', type=obj.get_type().typename(), msg=str(obj),
                        loc='%s:%s' % (module.get_name(), lineno))
    return


##  ExceptionCatcher
##
##  An ExceptionCatcher object represents a try...except block.
##  This is a specialized ExceptionFrame that is able to catch
##  specified exceptions. For each exception to be catched, an
##  ExceptionHandler object needs to be added by calling
##  add_handler().
##
class ExceptionCatcher(ExecutionFrame):

  nodes = None
  
  def __init__(self, parent):
    self.handlers = []
    self.received = set()
    ExecutionFrame.__init__(self, parent, None)
    ExceptionCatcher.nodes.append(self)
    return

  def __repr__(self):
    s = ', '.join(map(repr, self.handlers))
    x = self.getloc()
    if x:
      (module,lineno) = x
      return '<catch %s at %s:%s>' % (s, module.get_name(), lineno)
    else:
      return '<Catch %s at ???>' % s
  
  def add_handler(self, src):
    handler = ExceptionHandler(self, src)
    self.handlers.append(handler)
    return handler

  @classmethod
  def reset(klass):
    klass.nodes = []
    return
  
  @classmethod
  def check(klass):
    for node in klass.nodes:
      node.check_expt()
    return

  def recv(self, src):
    for obj in src:
      assert isinstance(obj, TracebackObject), obj
      self.received.add(obj)
    return

  def check_expt(self):
    for obj in self.received:
      for frame in self.handlers:
        if frame.handle_expt(obj.exptobj): break
      else:
        self.update_type(obj)
    return


##  ExceptionHandler
##
##  An ExceptionHandler object represents an "except" clause.
##
class ExceptionHandler(ExecutionFrame):

  def __init__(self, parent, expt):
    self.received = set()
    self.reraise = False
    self.var = CompoundTypeNode()
    if expt:
      self.expt = CompoundTypeNode()
      expt.connect(self.recv_expt)
    else:
      self.expt = None
    ExecutionFrame.__init__(self, parent, None)
    return

  def __repr__(self):
    return '<Handler %r>' % self.expt

  def recv_expt(self, src):
    from pyntch.aggregate_types import TupleType
    for obj in src:
      if obj in self.received: continue
      self.received.add(obj)
      if obj.is_type(TupleType.get_typeobj()):
        obj.elemall.connect(self.expt.recv)
      else:
        obj.connect(self.expt.recv)
    return

  def set_reraise(self):
    self.reraise = True
    return

  def handle_expt(self, obj):
    handled = True
    if self.expt:
      for typeobj in self.expt:
        if obj.is_type(typeobj): break
      else:
        handled = False
      if handled:
        obj.connect(self.var.recv)
        return not self.reraise
    return False


##  ExceptionMaker
##
##  Special behaviour on raising an exception.
##
class ExceptionMaker(CompoundTypeNode):
  
  def __init__(self, frame, anchor, exctype, excargs):
    self.frame = frame
    self.anchor = anchor
    self.exctype = exctype
    self.excargs = excargs
    self.processed = set()
    CompoundTypeNode.__init__(self)
    exctype.connect(self.recv_type)
    return
  
  def __repr__(self):
    return '<exceptionmaker %d>' % len(self.types)

  def recv_type(self, src):
    from pyntch.klass import ClassType
    from pyntch.config import ErrorConfig
    for obj in src:
      if obj in self.processed: continue
      self.processed.add(obj)
      # Instantiate an object only if it is a class object.
      # Otherwise, just return the object given.
      if isinstance(obj, ClassType):
        try:
          result = obj.call(self.frame, self.anchor, self.excargs, {})
        except NodeTypeError:
          self.frame.raise_expt(ErrorConfig.NotCallable(obj))
          continue
        self.frame.raise_expt(result)
      else:
        self.frame.raise_expt(obj)
    return
