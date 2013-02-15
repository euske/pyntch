#!/usr/bin/env python

from pyntch.typenode import CompoundTypeNode, NodeTypeError, NodeAttrError, NodeAssignError, UndefinedTypeNode, Element
from pyntch.typenode import BuiltinObject, BuiltinType, BuiltinCallable, BuiltinMethod, BuiltinConstMethod
from pyntch.typenode import TypeChecker
from pyntch.exception import StopIterationType
from pyntch.frame import ExceptionCatcher
from pyntch.basic_types import BoolType, IntType, StrType, NoneType, ANY
from pyntch.expression import IterElement, MethodCall
from pyntch.config import ErrorConfig


##  BuiltinAggregateObject
##
class BuiltinAggregateObject(BuiltinObject):

  def __init__(self, typeobj):
    self.attrs = {}
    BuiltinObject.__init__(self, typeobj)
    return

  def get_attr(self, frame, anchor, name, write=False):
    if write: raise NodeAssignError(name)
    if name in self.attrs:
      attr = self.attrs[name]
    else:
      attr = self.create_attr(frame, anchor, name)
      self.attrs[name] = attr
    return attr


##  BuiltinAggregateType
##
class BuiltinAggregateType(BuiltinCallable, BuiltinType):

  def __init__(self):
    self.cache_copy = {}
    self.cache_conv = {}
    self.nullobj = None
    BuiltinType.__init__(self)
    BuiltinCallable.__init__(self, self.TYPE_NAME, [], [ANY])
    return
  
  @classmethod
  def create_null(klass, frame, anchor):
    raise NotImplementedError

  @classmethod
  def create_copy(klass, frame, anchor, src):
    raise NotImplementedError
  
  @classmethod
  def create_sequence(klass, frame, anchor, src):
    raise NotImplementedError
  


##  BuiltinSequenceObject
##
class BuiltinSequenceObject(BuiltinAggregateObject):

  # SequenceExtender
  class SequenceExtender(BuiltinConstMethod):
    
    def __init__(self, name, target, retobj=NoneType.get_object(), args=None, optargs=None):
      self.target = target
      self.cache_extend = {}
      BuiltinConstMethod.__init__(self, name, retobj, args=args, optargs=optargs)
      return
    
    def __repr__(self):
      return '%r.extend' % self.target
    
    def accept_arg(self, frame, anchor, i, arg1):
      if arg1 in self.cache_extend:
        elem = self.cache_extend[arg1]
      else:
        elem = IterElement(frame, anchor, arg1)
        self.cache_extend[arg1] = elem
      elem.connect(self.target.elemall.recv)
      return

  # SequenceAppender
  class SequenceAppender(BuiltinConstMethod):
    
    def __init__(self, name, target, retobj=NoneType.get_object(), args=None, optargs=None):
      self.target = target
      BuiltinConstMethod.__init__(self, name, retobj, args=args, optargs=optargs)
      return
    
    def __repr__(self):
      return '%r.append' % self.target
    
    def accept_arg(self, frame, anchor, i, arg1):
      arg1.connect(self.target.elemall.recv)
      return

  # BuiltinSequenceObject
  def __init__(self, typeobj, elemall=None):
    self.elemall = CompoundTypeNode()
    if elemall:
      elemall.connect(self.elemall.recv)
    self.iter = None
    BuiltinAggregateObject.__init__(self, typeobj)
    return
  
  def get_iter(self, frame, anchor):
    if not self.iter:
      self.iter = IterType.create_iter(self.elemall)
    return self.iter

  def get_length(self, frame, anchor):
    return IntType.get_object()

  get_reversed = get_iter

  def connect_element(self, seqobj):
    assert isinstance(seqobj, BuiltinSequenceObject)
    self.elemall.connect(seqobj.elemall.recv)
    return

##  BuiltinSequenceType
##
class BuiltinSequenceType(BuiltinAggregateType):
  
  def process_args(self, frame, anchor, args, kwargs):
    if kwargs:
      frame.raise_expt(ErrorConfig.NoKeywordArgs())
      return UndefinedTypeNode.get_object()
    if args:
      return self.create_sequence(frame, anchor, args[0])
    return self.create_null(frame, anchor)


##  List
##
class ListObject(BuiltinSequenceObject):

  # InsertMethod
  class InsertMethod(BuiltinSequenceObject.SequenceAppender):
    
    def accept_arg(self, frame, anchor, i, arg1):
      if i == 0:
        BuiltinConstMethod.accept_arg(self, frame, anchor, i, arg1)
      else:
        BuiltinSequenceObject.SequenceAppender.accept_arg(self, frame, anchor, i, arg1)
      return

  # SortMethod
  class SortMethod(BuiltinConstMethod):
    
    class FuncChecker(CompoundTypeNode):
      
      def __init__(self, frame, anchor, target, fcmp, fkey):
        self.frame = frame
        self.anchor = anchor
        self.target = target
        self.received_fkey = set()
        self.received_fcmp = set()
        self.key = CompoundTypeNode()
        CompoundTypeNode.__init__(self)
        if fkey:
          fkey.connect(self.recv_fkey)
        else:
          target.elemall.connect(self.key.recv)
        if fcmp:
          fcmp.connect(self.recv_fcmp)
        return
      
      def recv_fkey(self, src):
        for obj in src:
          if obj in self.received_fkey: continue
          self.received_fkey.add(obj)
          try:
            obj.call(self.frame, self.anchor, (self.target.elemall,), {}).connect(self.key.recv)
          except NodeTypeError:
            self.frame.raise_expt(ErrorConfig.NotCallable(obj))
        return
      
      def recv_fcmp(self, src):
        for obj in src:
          if obj in self.received_fcmp: continue
          self.received_fcmp.add(obj)
          try:
            checker = TypeChecker(self.frame, IntType.get_typeobj(),
                                  'the return value of comparison function')
            obj.call(self.frame, self.anchor, (self.key, self.key), {}).connect(checker.recv)
          except NodeTypeError:
            self.frame.raise_expt(ErrorConfig.NotCallable(obj))
        return

    def __init__(self, name, target):
      self.target = target
      BuiltinConstMethod.__init__(self, name, NoneType.get_object(), [], [ANY,ANY,ANY])
      return
    
    def process_args(self, frame, anchor, args, kwargs):
      params = dict.fromkeys(['cmp', 'key', 'reverse'])
      args = list(args)
      if args:
        params['cmp'] = args.pop(0)
      if args:
        params['key'] = args.pop(0)
      if args:
        params['reserved'] = args.pop(0)
      for (k,v) in kwargs.iteritems():
        if k in params:
          if params[k] != None:
            frame.raise_expt(ErrorConfig.NoKeywordArg1(k))
          else:
            params[k] = v
        else:
          frame.raise_expt(ErrorConfig.NoKeywordArg1(k))
      self.FuncChecker(frame, anchor, self.target, params['cmp'], params['key'])
      return NoneType.get_object()

  # ListObject
  def __repr__(self):
    return '[%r]' % self.elemall
  def __str__(self):
    return self.desctxt({})

  def desctxt(self, done):
    if self in done:
      return '...'
    else:
      done[self] = len(done)
      return '[%s]' % self.elemall.desctxt(done)
    
  def descxml(self, done):
    if self in done:
      e = Element('ref', id=str(done[self]))
    else:
      done[self] = len(done)
      e = Element('list', id=str(done[self]))
      e.append(self.elemall.descxml(done))
    return e

  def get_element(self, frame, anchor, sub, write=False):
    frame.raise_expt(ErrorConfig.MaybeOutOfRange())
    return self.elemall

  def get_slice(self, frame, anchor, subs, write=False):
    frame.raise_expt(ErrorConfig.MaybeOutOfRange())
    return self
  
  def create_attr(self, frame, anchor, name):
    if name == 'append':
      return self.SequenceAppender('list.append', self, args=[ANY])
    elif name == 'count':
      return BuiltinConstMethod('list.count', IntType.get_object(), [ANY])
    elif name == 'extend':
      return self.SequenceExtender('list.extend', self, args=[ANY])
    elif name == 'index':
      return BuiltinConstMethod('list.index', IntType.get_object(), [ANY], [IntType, IntType],
                                expts=[ErrorConfig.MaybeElementNotFound()])
    elif name == 'insert':
      return self.InsertMethod('list.insert', self, [IntType, ANY])
    elif name == 'pop':
      return BuiltinConstMethod('list.pop', self.elemall, [], [IntType],
                                expts=[ErrorConfig.MaybeElementNotRemovable()])
    elif name == 'remove':
      return BuiltinConstMethod('list.remove', NoneType.get_object(), [ANY],
                                expts=[ErrorConfig.MaybeElementNotRemovable()])
    elif name == 'reverse':
      return BuiltinConstMethod('list.remove', NoneType.get_object())
    elif name == 'sort':
      return self.SortMethod('list.sort', self)
    raise NodeAttrError(name)


##  ListType
##
class ListType(BuiltinSequenceType):
  
  TYPE_NAME = 'list'
  CACHE = {}
  
  @classmethod
  def create_list(klass, elemall=None):
    return ListObject(klass.get_typeobj(), elemall=elemall)

  @classmethod
  def create_null(klass, frame, anchor):
    k = ('null',anchor)
    if k in klass.CACHE:
      return klass.CACHE[k]
    listobj = klass.create_list()
    klass.CACHE[k] = listobj
    return listobj

  @classmethod
  def create_copy(klass, frame, anchor, src):
    k = ('copy',anchor)
    if k in klass.CACHE:
      return klass.CACHE[k]
    listobj = klass.create_list(src.elemall)
    klass.CACHE[k] = listobj
    return listobj
    
  @classmethod
  def create_sequence(klass, frame, anchor, src):
    k = ('sequence',anchor)
    if k in klass.CACHE:
      return klass.CACHE[k]
    listobj = klass.create_list()
    IterElement(frame, anchor, src).connect(listobj.elemall.recv)
    klass.CACHE[k] = listobj
    return listobj

  
##  TupleObject
##
class TupleObject(BuiltinSequenceObject):
  
  def __init__(self, typeobj, elements=None, elemall=None):
    self.elements = elements
    if elements != None:
      elemall = CompoundTypeNode(elements)
    BuiltinSequenceObject.__init__(self, typeobj, elemall)
    return

  def __repr__(self):
    if self.elements == None:
      return '(*%r)' % self.elemall
    else:
      return '(%s)' % ','.join( repr(obj) for obj in self.elements )
  def __str__(self):
    return self.desctxt({})

  def desctxt(self, done):
    if self in done:
      return '...'
    else:
      done[self] = len(done)
      if self.elements == None:
        return '(*%s)' % self.elemall.desctxt(done)
      else:
        return '(%s)' % ','.join( obj.desctxt(done) for obj in self.elements )
      
  def descxml(self, done):
    if self in done:
      e = Element('ref', id=str(done[self]))
    else:
      done[self] = len(done)
      e = Element('tuple', id=str(done[self]))
      if self.elements == None:
        e.append(self.elemall.descxml(done))
      else:
        e.set('len', str(len(self.elements)))
        for obj in self.elements:
          e.append(obj.descxml(done))
    return e

  def get_element(self, frame, anchor, sub, write=False):
    if write: raise NodeAssignError
    frame.raise_expt(ErrorConfig.MaybeOutOfRange())
    return self.elemall

  def get_slice(self, frame, anchor, subs, write=False):
    if write: raise NodeAssignError
    frame.raise_expt(ErrorConfig.MaybeOutOfRange())
    return self
  
  def create_attr(self, frame, anchor, name):
    raise NodeAttrError(name)


##  TupleType
##
class TupleType(BuiltinSequenceType):
  
  TYPE_NAME = 'tuple'
  CACHE = {}
    
  @classmethod
  def create_tuple(klass, elements=None, elemall=None):
    return TupleObject(klass.get_typeobj(), elements=elements, elemall=elemall)
  
  @classmethod
  def create_null(klass, frame, anchor):
    k = ('null',anchor)
    if k in klass.CACHE:
      return klass.CACHE[k]
    tupleobj = klass.create_tuple()
    klass.CACHE[k] = tupleobj
    return tupleobj

  @classmethod
  def create_copy(klass, frame, anchor, src):
    k = ('copy',anchor)
    if k in klass.CACHE:
      return klass.CACHE[k]
    tupleobj = klass.create_tuple(elements=src.elements, elemall=src.elemall)
    klass.CACHE[k] = tupleobj
    return tupleobj
    
  @classmethod
  def create_sequence(klass, frame, anchor, src):
    k = ('sequence',anchor)
    if k in klass.CACHE:
      return klass.CACHE[k]
    tupleobj = klass.create_tuple()
    IterElement(frame, anchor, src).connect(tupleobj.elemall.recv)
    klass.CACHE[k] = tupleobj
    return tupleobj


##  FrozenSetObject
##
class FrozenSetObject(BuiltinSequenceObject):

  # Intersection
  class Intersection(BuiltinConstMethod):
    
    class TypeMixer(CompoundTypeNode):
      
      def __init__(self, frame, anchor, target, src1, src2):
        self.frame = frame
        self.anchor = anchor
        self.target = target
        self.types1 = CompoundTypeNode()
        self.types2 = CompoundTypeNode()
        CompoundTypeNode.__init__(self)
        src1.connect(self.recv1)
        src2.connect(self.recv2)
        return
      
      def recv1(self, src):
        for obj in src:
          IterElement(self.frame, self.anchor, obj).connect(self.types1.recv)
        self.update_intersection()
        return
      
      def recv2(self, src):
        for obj in src:
          IterElement(self.frame, self.anchor, obj).connect(self.types2.recv)
        self.update_intersection()
        return
        
      def update_intersection(self):
        for obj1 in self.types1:
          for obj2 in self.types2:
            if obj1.get_type() == obj2.get_type():
              obj1.connect(self.target.elemall.recv)
              obj2.connect(self.target.elemall.recv)
        return
      
    def __init__(self, name, src1):
      self.src1 = src1
      BuiltinConstMethod.__init__(self, name, SetType.create_set(), [ANY])
      return
    
    def __repr__(self):
      return '%r.intersection' % self.src1
    
    def process_args(self, frame, anchor, args, kwargs):
      if kwargs or len(args) != 1:
        return BuiltinConstMethod.process_args(self, frame, anchor, args, kwargs)
      self.TypeMixer(frame, anchor, self.retobj, self.src1, args[0])
      return self.retobj

  #
  def __repr__(self):
    return '([%r])' % self.elemall
  def __str__(self):
    return self.desctxt({})
  
  def desctxt(self, done):
    if self in done:
      return '...'
    else:
      done[self] = len(done)
      return '([%s])' % self.elemall.desctxt(done)
    
  def descxml(self, done):
    if self in done:
      e = Element('ref', id=str(done[self]))
    else:
      done[self] = len(done)
      e = Element('set', id=str(done[self]))
      e.append(self.elemall.descxml(done))
    return e

  def create_attr(self, frame, anchor, name):
    if name == 'copy':
      setobj = self.get_type().create_copy(frame, anchor, self)
      return BuiltinConstMethod('set.copy', setobj)
    elif name == 'difference':
      setobj = self.get_type().create_copy(frame, anchor, self)
      return BuiltinConstMethod('set.difference', setobj, [[ANY]])
    elif name == 'intersection':
      return SetObject.Intersection('set.intersection', self)
    elif name == 'issubset':
      return BuiltinConstMethod('set.issubset', BoolType.get_object(), [[ANY]])
    elif name == 'issuperset':
      return BuiltinConstMethod('set.issuperset', BoolType.get_object(), [[ANY]])
    elif name == 'symmetric_difference':
      setobj = self.get_type().create_copy(frame, anchor, self)
      return self.SequenceExtender('set.symmetric_difference', setobj, setobj, [ANY])
    elif name == 'union':
      setobj = self.get_type().create_copy(frame, anchor, self)
      return self.SequenceExtender('set.union', setobj, setobj, [ANY])
    raise NodeAttrError(name)
  

##  FrozenSetType
##
class FrozenSetType(BuiltinSequenceType):

  TYPE_NAME = 'frozenset'
  CACHE = {}

  @classmethod
  def create_set(klass, elemall=None):
    return FrozenSetObject(klass.get_typeobj(), elemall=elemall)

  @classmethod
  def create_null(klass, frame, anchor):
    k = ('null',anchor)
    if k in klass.CACHE:
      return klass.CACHE[k]
    setobj = klass.create_set()
    klass.CACHE[k] = setobj
    return setobj

  @classmethod
  def create_copy(klass, frame, anchor, src):
    k = ('copy',anchor)
    if k in klass.CACHE:
      return klass.CACHE[k]
    setobj = klass.create_set(src.elemall)
    klass.CACHE[k] = setobj
    return setobj
    
  @classmethod
  def create_sequence(klass, frame, anchor, src):
    k = ('sequence',anchor)
    if k in klass.CACHE:
      return klass.CACHE[k]
    setobj = klass.create_set()
    IterElement(frame, anchor, src).connect(setobj.elemall.recv)
    klass.CACHE[k] = setobj
    return setobj


##  SetObject
##
class SetObject(FrozenSetObject):

  def create_attr(self, frame, anchor, name):
    if name == 'add':
      return self.SequenceAppender('set.add', self, args=[ANY])
    elif name == 'clear':
      return BuiltinConstMethod('set.clear', NoneType.get_object())
    elif name == 'difference_update':
      return BuiltinConstMethod('set.difference_update', NoneType.get_object(), [[ANY]])
    elif name == 'discard':
      return BuiltinConstMethod('set.discard', NoneType.get_object(), [ANY])
    elif name == 'intersection_update':
      return BuiltinConstMethod('set.intersection_update', NoneType.get_object(), [[ANY]])
    elif name == 'pop':
      return BuiltinConstMethod('set.pop', NoneType.get_object(), 
                                expts=[ErrorConfig.MaybeElementNotRemovable()])
    elif name == 'remove':
      return BuiltinConstMethod('set.remove', NoneType.get_object(), [ANY],
                                expts=[ErrorConfig.MaybeElementNotFound()])
    elif name == 'symmetric_difference_update':
      return self.SequenceExtender('set.symmetric_difference_update', self, args=[ANY])
    elif name == 'update':
      return self.SequenceExtender('set.update', self, self, [ANY])
    return FrozenSetObject.create_attr(self, frame, anchor, name)
  

##  SetType
##
class SetType(FrozenSetType):

  TYPE_NAME = 'set'

  @classmethod
  def create_set(klass, elemall=None):
    return SetObject(klass.get_typeobj(), elemall=elemall)


##  IterObject
##
class IterObject(BuiltinAggregateObject):

  def __init__(self, typeobj, elemall=None):
    self.elemall = CompoundTypeNode()
    if elemall:
      elemall.connect(self.elemall.recv)
    BuiltinAggregateObject.__init__(self, typeobj)
    return
  
  def __repr__(self):
    return '(%r, ...)' % self.elemall
  def __str__(self):
    return self.desctxt({})

  def desctxt(self, done):
    if self in done:
      return '...'
    else:
      done[self] = len(done)
      return '(%s, ...)' % self.elemall.desctxt(done)
    
  def descxml(self, done):
    if self in done:
      e = Element('ref', id=str(done[self]))
    else:
      done[self] = len(done)
      e = Element('iter', id=str(done[self]))
      e.append(self.elemall.descxml(done))
    return e

  def get_iter(self, frame, anchor):
    return self

  def create_attr(self, frame, anchor, name):
    if name == 'next':
      return BuiltinConstMethod('iter.next', self.elemall,
                                expts=[StopIterationType.maybe('might raise StopIteration')])
    raise NodeAttrError(name)
  

##  IterType
##
class IterType(BuiltinType):

  TYPE_NAME = 'iterator'

  @classmethod
  def create_iter(klass, elemall=None):
    return IterObject(klass.get_typeobj(), elemall=elemall)


##  ReversedType
##
class ReversedType(BuiltinCallable, IterType):

  TYPE_NAME = 'reversed'

  # convert
  class ReversedIterConverter(CompoundTypeNode):
    
    def __init__(self, frame, anchor, target):
      self.frame = frame
      self.anchor = anchor
      self.target = target
      self.received = set()
      CompoundTypeNode.__init__(self)
      target.connect(self.recv_target)
      return
    
    def __repr__(self):
      return 'reversed(%r)' % self.target
    
    def recv_target(self, src):
      for obj in src:
        if obj in self.received: continue
        self.received.add(obj)
        try:
          iterobj = obj.get_reversed(self.frame, self.anchor)
          frame1 = ExceptionCatcher(self.frame)
          frame1.add_handler(StopIterationType.get_typeobj())
          MethodCall(frame1, self.anchor, iterobj, 'next').connect(self.recv)
        except NodeTypeError:
          self.frame.raise_expt(ErrorConfig.NotIterable(obj))
      return
  
  def __init__(self):
    BuiltinType.__init__(self)
    BuiltinCallable.__init__(self, self.TYPE_NAME, [ANY])
    return

  def process_args(self, frame, anchor, args, kwargs):
    if kwargs:
      frame.raise_expt(ErrorConfig.NoKeywordArgs())
      return UndefinedTypeNode.get_object()
    return self.ReversedIterConverter(frame, anchor, args[0])
  

##  GeneratorObject
##
class GeneratorSlot(CompoundTypeNode):
  
  def __init__(self, value):
    self.received = CompoundTypeNode()
    CompoundTypeNode.__init__(self, [value])
    return

class GeneratorObject(IterObject):

  # Send
  class Send(BuiltinConstMethod):
    
    def __init__(self, name, target, retobj=NoneType.get_object(), args=None, expts=None):
      self.target = target
      BuiltinConstMethod.__init__(self, name, retobj, args=args, expts=expts)
      return
    
    def accept_arg(self, frame, anchor, i, arg1):
      arg1.connect(self.target.sent.recv)
      return

  # GeneratorObject
  def __init__(self, typeobj, elemall=None, elements=None):
    IterObject.__init__(self, typeobj, elemall=elemall)
    self.sent = CompoundTypeNode()
    if elements:
      for obj in elements:
        if isinstance(obj, GeneratorSlot):
          self.sent.connect(obj.received.recv)
        obj.connect(self.elemall.recv)
    return

  def create_attr(self, frame, anchor, name):
    if name == 'send':
      return self.Send('generator.send', self, self.elemall, [ANY],
                       expts=[StopIterationType.maybe('might raise StopIteration')])
    if name == 'next':
      NoneType.get_object().connect(self.sent.recv)
      return self.Send('generator.next', self, self.elemall,
                       expts=[StopIterationType.maybe('might raise StopIteration')])
    if name == 'throw':
      # XXX do nothing for now
      return BuiltinConstMethod('generator.throw', NoneType.get_object(), [ANY], [ANY, ANY])
    if name == 'close':
      return self.Send('generator.close', self, NoneType.get_object(), [ANY])
    return IterObject.create_attr(self, frame, anchor, name)


##  GeneratorType
##
class GeneratorType(IterType):

  TYPE_NAME = 'generator'

  @classmethod
  def create_slot(klass, value):
    return GeneratorSlot(value)

  @classmethod
  def create_generator(klass, elements):
    return GeneratorObject(klass.get_typeobj(), elements=elements)


##  DictObject
##
class DictObject(BuiltinAggregateObject):

  # convert
  class DictConverter(CompoundTypeNode):
    
    def __init__(self, frame, anchor, target):
      self.frame = frame
      self.anchor = anchor
      self.target = target
      CompoundTypeNode.__init__(self)
      return
    
    def __repr__(self):
      return 'convert(%r)' % self.target
    
    def recv(self, src):
      for obj in src:
        IterElement(self.frame, self.anchor, obj).connect(self.recv_pair)
      return
  
    def recv_pair(self, src):
      for obj in src:
        if obj.is_type(TupleType.get_typeobj()) and obj.elements:
          if len(obj.elements) == 2:
            (k,v) = obj.elements
            k.connect(self.target.key.recv)
            v.connect(self.target.value.recv)
          else:
            self.frame.raise_expt(ErrorConfig.NotConvertable('(key,value)'))
          continue
        elem = IterElement(self.frame, self.anchor, obj)
        elem.connect(self.target.key.recv)
        elem.connect(self.target.value.recv)
        self.frame.raise_expt(ErrorConfig.NotConvertable('dict'))
      return
    
  # fromkeys
  class DictConverterFromKeys(CompoundTypeNode):
    
    def __init__(self, frame, anchor, target):
      self.frame = frame
      self.anchor = anchor
      self.target = target
      CompoundTypeNode.__init__(self)
      return
    
    def recv(self, src):
      for obj in src:
        IterElement(self.frame, self.anchor, obj).connect(self.target.key.recv)
      return

  # dict.get
  class Get(BuiltinConstMethod):
    
    def __init__(self, dictobj, name):
      self.dictobj = dictobj
      self.found = CompoundTypeNode([dictobj.value])
      BuiltinConstMethod.__init__(self, name, self.found, [ANY], [ANY])
      return
    
    def process_args(self, frame, anchor, args, kwargs):
      if len(args) == 1:
        self.found.update_type(NoneType.get_object())
      return BuiltinConstMethod.process_args(self, frame, anchor, args, kwargs)
    
    def accept_arg(self, frame, anchor, i, arg1):
      if i != 0:
        arg1.connect(self.found.recv)
      return

  # dict.pop
  class Pop(BuiltinConstMethod):
    
    def __init__(self, dictobj, name):
      self.dictobj = dictobj
      self.found = CompoundTypeNode([dictobj.value])
      BuiltinConstMethod.__init__(self, name, self.found, [ANY], [ANY])
      return
    
    def process_args(self, frame, anchor, args, kwargs):
      if len(args) == 1:
        frame.raise_expt(ErrorConfig.MaybeKeyNotFound())
      return BuiltinConstMethod.process_args(self, frame, anchor, args, kwargs)
    
    def accept_arg(self, frame, anchor, i, arg1):
      if i != 0:
        arg1.connect(self.found.recv)
      return

  # dict.setdefault
  class SetDefault(BuiltinConstMethod):
    
    def __init__(self, dictobj, name):
      self.dictobj = dictobj
      self.found = CompoundTypeNode([dictobj.value])
      BuiltinConstMethod.__init__(self, name, self.found, [ANY], [ANY])
      return
    
    def __repr__(self):
      return '%r.setdefault' % self.dictobj
    
    def process_args(self, frame, anchor, args, kwargs):
      if len(args) == 1:
        self.found.update_type(NoneType.get_object())
      return BuiltinConstMethod.process_args(self, frame, anchor, args, kwargs)
    
    def accept_arg(self, frame, anchor, i, arg1):
      if i == 0:
        arg1.connect(self.dictobj.value.recv)
      else:
        arg1.connect(self.found.recv)
      return

  # dict.update
  class Update(BuiltinConstMethod):
    
    def __init__(self, dictobj, name):
      self.cache_update = {}
      self.dictobj = dictobj
      BuiltinConstMethod.__init__(self, name, NoneType.get_object(), [ANY])
      return
    
    def process_args(self, frame, anchor, args, kwargs):
      v = args[0]
      if v not in self.cache_update:
        converter = DictObject.DictConverterFromKeys(frame, anchor, self.dictobj)
        self.cache_update[v] = converter
        v.connect(converter.recv)
      return NoneType.get_object()

  # DictObject
  def __init__(self, typeobj, items=None, key=None, value=None):
    if items != None:
      assert key == None and value == None
      self.key = CompoundTypeNode( k for (k,v) in items )
      self.value = CompoundTypeNode( v for (k,v) in items )
    else:
      self.key = CompoundTypeNode(key)
      self.value = CompoundTypeNode(value)
    self.default = CompoundTypeNode([NoneType.get_object()])
    self.value.connect(self.default.recv)
    self.iter = None
    BuiltinAggregateObject.__init__(self, typeobj)
    return
  
  def __repr__(self):
    return '{%r: %r}' % (self.key, self.value)
  def __str__(self):
    return self.desctxt({})

  def desctxt(self, done):
    if self in done:
      return '...'
    else:
      done[self] = len(done)
      return '{%s: %s}' % (self.key.desctxt(done), self.value.desctxt(done))
    
  def descxml(self, done):
    if self in done:
      e = Element('ref', id=str(done[self]))
    else:
      done[self] = len(done)
      e = Element('dict', id=str(done[self]))
      e.append(self.key.descxml(done))
      e.append(self.value.descxml(done))
    return e

  def create_attr(self, frame, anchor, name):
    if name == 'clear':
      return BuiltinConstMethod('dict.clear', NoneType.get_object())
    elif name == 'copy':
      dictobj = self.get_type().create_copy(frame, anchor, self)
      return BuiltinConstMethod('dict.copy', dictobj)
    elif name == 'fromkeys':
      return DictType.FromKeys('dict.fromkeys')
    elif name == 'get':
      return DictObject.Get(self, 'dict.get')
    elif name == 'has_key':
      return BuiltinConstMethod('dict.has_key', BoolType.get_object(), [ANY])
    elif name == 'keys':
      return BuiltinConstMethod('dict.keys',
                                  ListType.create_list(self.key))
    elif name == 'values':
      return BuiltinConstMethod('dict.values',
                                  ListType.create_list(self.value))
    elif name == 'items':
      return BuiltinConstMethod('dict.items',
                                  ListType.create_list(TupleType.create_tuple([self.key, self.value])))
    elif name == 'iterkeys':
      return BuiltinConstMethod('dict.iterkeys',
                                  IterType.create_iter(self.key))
    elif name == 'itervalues':
      return BuiltinConstMethod('dict.itervalues',
                                  IterType.create_iter(self.value))
    elif name == 'iteritems':
      return BuiltinConstMethod('dict.iteritems',
                                  IterType.create_iter(TupleType.create_tuple([self.key, self.value])))
    elif name == 'pop':
      return DictObject.Pop(self, 'dict.pop')
    elif name == 'popitem':
      return BuiltinConstMethod('dict.popitem', TupleType.create_tuple([self.key, self.value]),
                                expts=[ErrorConfig.MaybeElementNotFound()])
    elif name == 'setdefault':
      return DictObject.SetDefault(self, 'dict.setdefault')
    elif name == 'update':
      return DictObject.Update(self, 'dict.update')
    raise NodeAttrError(name)

  def get_element(self, frame, anchor, key, write=False):
    if write:
      key.connect(self.key.recv)
    else:
      frame.raise_expt(ErrorConfig.MaybeKeyNotFound())
    return self.value

  def get_iter(self, frame, anchor):
    if not self.iter:
      self.iter = IterType.create_iter(self.key)
    return self.iter

  def get_length(self, frame, anchor):
    return IntType.get_object()


##  DictType
##
class DictType(BuiltinAggregateType):
  
  TYPE_NAME = 'dict'
  CACHE = {}

  # dict.fromkeys
  class FromKeys(BuiltinConstMethod):
    
    def __init__(self, name):
      self.cache_fromkeys = {}
      self.dictobj = DictType.create_dict()
      BuiltinConstMethod.__init__(self, name, self.dictobj, [ANY], [ANY])
      return
    
    def process_args(self, frame, anchor, args, kwargs):
      if 2 <= len(args):
        args[1].connect(self.dictobj.value.recv)
      else:
        NoneType.get_object().connect(self.dictobj.value.recv)
      v = args[0]
      if v not in self.cache_fromkeys:
        converter = DictObject.DictConverterFromKeys(frame, anchor, self.dictobj)
        self.cache_fromkeys[v] = converter
        v.connect(converter.recv)
      return self.dictobj
    
  @classmethod
  def create_dict(klass, items=None, key=None, value=None):
    return DictObject(klass.get_typeobj(), items=items, key=key, value=value)

  @classmethod
  def create_null(klass, frame, anchor):
    k = ('null',anchor)
    if k in klass.CACHE:
      return klass.CACHE[k]
    dictobj = klass.create_dict()
    klass.CACHE[k] = dictobj
    return dictobj

  @classmethod
  def create_copy(klass, frame, anchor, src):
    k = ('copy',anchor)
    if k in klass.CACHE:
      return klass.CACHE[k]
    dictobj = klass.create_dict(key=[src.key], value=[src.value])
    klass.CACHE[k] = dictobj
    return dictobj

  @classmethod
  def create_sequence(klass, frame, anchor, src):
    k = ('sequence',anchor)
    if k in klass.CACHE:
      return klass.CACHE[k]
    dictobj = klass.create_dict()
    converter = DictObject.DictConverter(frame, anchor, dictobj)
    src.connect(converter.recv)
    klass.CACHE[k] = dictobj
    return dictobj

  def process_args(self, frame, anchor, args, kwargs):
    if kwargs:
      node = tuple(kwargs.values())
      if node in self.cache_conv:
        obj = self.cache_conv[node]
      else:
        obj = DictType.create_dict(key=[StrType.get_object()], value=kwargs.values())
        self.cache_conv[node] = obj
      return obj
    if args:
      return self.create_sequence(frame, anchor, args[0])
    return self.create_null(frame, anchor)

  def get_attr(self, frame, anchor, name, write=False):
    if name == 'fromkeys' and not write:
      return DictType.FromKeys('dict.fromkeys')
    return BuiltinAggregateType.get_attr(self, frame, anchor, name, write=write)


##  EnumerateType
##
class EnumerateType(BuiltinCallable, BuiltinType):

  def __init__(self):
    BuiltinType.__init__(self)
    BuiltinCallable.__init__(self, 'enumerate', [ANY])
    return

  def process_args(self, frame, anchor, args, kwargs):
    if kwargs:
      frame.raise_expt(ErrorConfig.NoKeywordArgs())
      return UndefinedTypeNode.get_object()
    elemall = TupleType.create_tuple([IntType.get_object(), IterElement(frame, anchor, args[0])])
    return IterObject(self.get_typeobj(), elemall=elemall)
