#!/usr/bin/env python

##  This module should not be imported as toplevel,
##  as it causes circular imports!

from pyntch.typenode import CompoundTypeNode, NodeTypeError, NodeAttrError, UndefinedTypeNode
from pyntch.typenode import BuiltinType, BuiltinCallable, BuiltinConstCallable
from pyntch.typenode import TypeChecker, SequenceTypeChecker, Element
from pyntch.basic_types import TypeType, NoneType, NumberType, BoolType, IntType, LongType, \
     FloatType, BaseStringType, StrType, UnicodeType, ANY
from pyntch.aggregate_types import ListType, TupleType, DictType, IterType, ListObject
from pyntch.expression import IterElement, IterRef, BinaryOp, MustBeDefinedNode, FunCall
from pyntch.config import ErrorConfig


##  BuiltinFunc
class BuiltinFunc(BuiltinCallable, BuiltinType):

  TYPE_NAME = 'builtinfunc'
  
  def __init__(self, name, args=None, optargs=None, expts=None):
    BuiltinCallable.__init__(self, name, args=args, optargs=optargs, expts=expts)
    BuiltinType.__init__(self)
    return
  
  def __repr__(self):
    return '<builtin %s>' % self.name

  def descxml(self, done):
    done[self] = len(done)
    return Element(self.get_type().typename(), name=self.name)


##  BuiltinFuncNoKwd
class BuiltinFuncNoKwd(BuiltinFunc):

  def process_args(self, frame, anchor, args, kwargs):
    if kwargs:
      frame.raise_expt(ErrorConfig.NoKeywordArgs())
      return UndefinedTypeNode.get_object()
    return self.process_args_nokwd(frame, anchor, args)

  def process_args_nokwd(self, frame, anchor, args):
    raise NotImplementedError


##  BuiltinConstFunc
class BuiltinConstFunc(BuiltinConstCallable, BuiltinType):

  TYPE_NAME = 'builtinfunc'

  def __init__(self, name, retobj, args=None, optargs=None, expts=None):
    BuiltinType.__init__(self)
    BuiltinConstCallable.__init__(self, name, retobj, args=args, optargs=optargs, expts=expts)
    return
  
  def __repr__(self):
    return '<builtin %s>' % self.name

  def descxml(self, done):
    done[self] = len(done)
    return Element(self.get_type().typename(), name=self.name)


##  IterFuncChecker
class IterFuncChecker(CompoundTypeNode):

  def __init__(self, frame, anchor, target, func):
    self.frame = frame
    self.anchor = anchor
    self.target = target
    CompoundTypeNode.__init__(self)
    func.connect(self.recv_func)
    return

  def recv_func(self, src):
    for obj in src:
      try:
        obj.call(self.frame, self.anchor, (self.target.elemall,))
      except NodeTypeError:
        self.frame.raise_expt(ErrorConfig.NotCallable(obj))
    return

##  TypeSpecChecker
class TypeSpecChecker(CompoundTypeNode):
  
  def __init__(self, frame, anchor, spec):
    self.checker = TypeChecker(frame, [TypeType.get_typeobj()], 'typespec')
    self.tuplechecker = SequenceTypeChecker(frame, anchor, [TypeType.get_typeobj()], 'typespec')
    CompoundTypeNode.__init__(self)
    spec.connect(self.recv)
    return

  def recv(self, src):
    for obj in src:
      if obj.is_type(TupleType.get_typeobj()):
        obj.connect(self.tuplechecker.recv)
      else:
        obj.connect(self.checker.recv)
    return


##  AbsFunc
##
class AbsFunc(BuiltinFuncNoKwd):

  def __init__(self):
    BuiltinFunc.__init__(self, 'abs', [NumberType])
    return

  def process_args_nokwd(self, frame, anchor, args):
    checker = TypeChecker(frame, [NumberType.get_typeobj()], 'arg 0')
    args[0].connect(checker.recv)
    return args[0]


##  ApplyFunc
##
class ApplyFunc(BuiltinFuncNoKwd):

  def __init__(self):
    BuiltinFunc.__init__(self, 'apply', [ANY], [ANY, ANY])
    return

  def process_args_nokwd(self, frame, anchor, args):
    star = dstar = None
    if 2 <= len(args):
      star = args[1]
    if 3 <= len(args):
      dstar = args[2]
    return FunCall(frame, anchor, args[0], star=star, dstar=dstar)


##  AllFunc, AnyFunc
##
class AllFunc(BuiltinConstFunc):

  def __init__(self, name='all'):
    BuiltinConstFunc.__init__(self, name, BoolType.get_object(), [ANY])
    return

  def accept_arg(self, frame, anchor, i, arg1):
    IterElement(frame, anchor, arg1)
    return 

class AnyFunc(AllFunc):

  def __init__(self):
    AllFunc.__init__(self, 'any')
    return


##  CallableFunc
##
class CallableFunc(BuiltinConstFunc):

  def __init__(self):
    BuiltinConstFunc.__init__(self, 'callable', BoolType.get_object(), [ANY])
    return


##  ChrFunc
##
class ChrFunc(BuiltinConstFunc):

  def __init__(self):
    BuiltinConstFunc.__init__(self, 'chr', StrType.get_object(),
                              [IntType])
    return


##  CmpFunc
##
class CmpFunc(BuiltinConstFunc):

  def __init__(self):
    BuiltinConstFunc.__init__(self, 'cmp', IntType.get_object(), [ANY, ANY])
    return


##  DirFunc
##
class DirFunc(BuiltinConstFunc):

  def __init__(self):
    BuiltinConstFunc.__init__(self, 'dir', ListType.create_list(StrType.get_object()), [], [ANY])
    return


##  DivmodFunc
##
class DivmodFunc(BuiltinFuncNoKwd):

  def __init__(self):
    BuiltinFunc.__init__(self, 'divmod', [NumberType, NumberType])
    return

  def process_args_nokwd(self, frame, anchor, args):
    checker = TypeChecker(frame, [NumberType.get_typeobj()], 'arg 0')
    args[0].connect(checker.recv)
    checker = TypeChecker(frame, [NumberType.get_typeobj()], 'arg 1')
    args[1].connect(checker.recv)
    obj = CompoundTypeNode(args)
    return TupleType.create_tuple([obj, obj])


##  FilterFunc
##
class FilterFunc(BuiltinFuncNoKwd):

  class FilterCaller(CompoundTypeNode):
    
    def __init__(self, frame, anchor, func, seq):
      self.frame = frame
      self.anchor = anchor
      self.received = set()
      self.elem = IterElement(frame, anchor, seq)
      CompoundTypeNode.__init__(self, [seq])
      func.connect(self.recv_func)
      return

    def recv_func(self, src):
      for obj in src:
        if obj in self.received: continue
        self.received.add(obj)
        if not isinstance(obj, NoneType):
          try:
            obj.call(self.frame, self.anchor, (self.elem,), {})
          except NodeTypeError:
            self.frame.raise_expt(ErrorConfig.NotCallable(obj))
      return
      
  def __init__(self):
    BuiltinFunc.__init__(self, 'filter', [ANY, ANY])
    return

  def process_args_nokwd(self, frame, anchor, args):
    return self.FilterCaller(frame, anchor, args[0], args[1])


##  HashFunc
##
class HashFunc(BuiltinConstFunc):

  def __init__(self):
    BuiltinConstFunc.__init__(self, 'hash', IntType.get_object(), [ANY])
    return


##  HexFunc
##
class HexFunc(BuiltinConstFunc):

  def __init__(self):
    BuiltinConstFunc.__init__(self, 'hex', StrType.get_object(), [IntType])
    return


##  IdFunc
##
class IdFunc(BuiltinConstFunc):

  def __init__(self):
    BuiltinConstFunc.__init__(self, 'id', IntType.get_object(), [ANY])
    return


##  IsInstanceFunc
##
class IsInstanceFunc(BuiltinConstFunc):

  def __init__(self):
    BuiltinConstFunc.__init__(self, 'isinstance', BoolType.get_object(), [ANY, ANY])
    return

  def accept_arg(self, frame, anchor, i, arg1):
    if i == 1:
      TypeSpecChecker(frame, anchor, arg1)
    return
    

##  IsSubclassFunc
##
class IsSubclassFunc(BuiltinConstFunc):

  def __init__(self):
    BuiltinConstFunc.__init__(self, 'issubclass', BoolType.get_object(), [TypeType, ANY])
    return

  def accept_arg(self, frame, anchor, i, arg1):
    if i == 1:
      TypeSpecChecker(frame, anchor, arg1)
    return
    

##  IterFunc
##
class IterFunc(BuiltinFuncNoKwd):

  def process_args_nokwd(self, frame, anchor, args):
    v = args[0]
    if v in self.cache:
      iterobj = self.cache[v]
    else:
      iterobj = IterRef(frame, anchor, v)
      self.cache[v] = iterobj
    return iterobj

  def __init__(self):
    self.cache = {}
    BuiltinFunc.__init__(self, 'iter', [ANY])
    return


##  LenFunc
##
class LenFunc(BuiltinFuncNoKwd):

  class LengthChecker(MustBeDefinedNode):
    
    def __init__(self, frame, anchor, target):
      self.received = set()
      self.target = target
      MustBeDefinedNode.__init__(self, frame, anchor)
      self.target.connect(self.recv_target)
      return

    def recv_target(self, src):
      for obj in src:
        if obj in self.received: continue
        self.received.add(obj)
        try:
          obj.get_length(self.frame, self.anchor).connect(self.recv)
        except (NodeTypeError, NodeAttrError):
          pass
      return

    def check_undefined(self):
      if not self.received: return
      if self.types: return
      self.raise_expt(ErrorConfig.NoLength(self.target))
      return

  def process_args_nokwd(self, frame, anchor, args):
    self.LengthChecker(frame, anchor, args[0])
    return IntType.get_object()
  
  def __init__(self):
    BuiltinFunc.__init__(self, 'len', [ANY])
    return


##  MapFunc
##
class MapFunc(BuiltinFunc):

  class MapCaller(CompoundTypeNode):
    
    def __init__(self, frame, anchor, func, objs):
      self.frame = frame
      self.anchor = anchor
      self.received = set()
      self.args = tuple( IterElement(frame, anchor, obj) for obj in objs )
      self.listobj = ListType.create_list()
      CompoundTypeNode.__init__(self, [self.listobj])
      func.connect(self.recv_func)
      return

    def recv_func(self, src):
      for obj in src:
        if obj in self.received: continue
        self.received.add(obj)
        try:
          obj.call(self.frame, self.anchor, self.args, {}).connect(self.listobj.elemall.recv)
        except NodeTypeError:
          self.frame.raise_expt(ErrorConfig.NotCallable(obj))
      return
      
  def __init__(self):
    BuiltinFunc.__init__(self, 'map', [ANY, ANY])
    return

  def call(self, frame, anchor, args, kwargs):
    if kwargs:
      frame.raise_expt(ErrorConfig.NoKeywordArgs())
      return UndefinedTypeNode.get_object()
    if len(args) < self.minargs:
      frame.raise_expt(ErrorConfig.InvalidNumOfArgs(self.minargs, len(args)))
      return UndefinedTypeNode.get_object()
    return self.MapCaller(frame, anchor, args[0], args[1:])


##  MinFunc, MaxFunc
##
class MinFunc(BuiltinFunc):

  def __init__(self, name='min'):
    BuiltinFunc.__init__(self, name, [ANY])
    return

  def call(self, frame, anchor, args, kwargs):
    if kwargs:
      frame.raise_expt(ErrorConfig.NoKeywordArgs())
      return UndefinedTypeNode.get_object()
    retobj = CompoundTypeNode()
    if len(args) == 1:
      IterElement(frame, anchor, args[0]).connect(retobj.recv)
    else:
      for arg1 in args:
        arg1.connect(retobj.recv)
    if 'key' in kwargs:
      IterFuncChecker(frame, anchor, retobj, kwargs['key'])
    return retobj
  
class MaxFunc(MinFunc):

  def __init__(self):
    MinFunc.__init__(self, 'max')
    return


##  OctFunc
##
class OctFunc(BuiltinConstFunc):

  def __init__(self):
    BuiltinConstFunc.__init__(self, 'oct', StrType.get_object(), [IntType])
    return


##  OrdFunc
##
class OrdFunc(BuiltinConstFunc):

  def __init__(self):
    BuiltinConstFunc.__init__(self, 'ord', IntType.get_object(),
                              [BaseStringType])
    return


##  PowFunc
##
class PowFunc(BuiltinFuncNoKwd):

  def __init__(self):
    BuiltinFunc.__init__(self, 'pow', [NumberType, NumberType], [NumberType])
    return

  def process_args_nokwd(self, frame, anchor, args):
    checker = TypeChecker(frame, [NumberType.get_typeobj()], 'arg 0')
    args[0].connect(checker.recv)
    checker = TypeChecker(frame, [NumberType.get_typeobj()], 'arg 1')
    args[1].connect(checker.recv)
    if 3 <= len(args):
      checker = TypeChecker(frame, [NumberType.get_typeobj()], 'arg 2')
      args[2].connect(checker.recv)
    return CompoundTypeNode(args)


##  RangeFunc
##
class RangeFunc(BuiltinConstFunc):

  def __init__(self):
    BuiltinConstFunc.__init__(self, 'range', ListType.create_list(IntType.get_object()), 
                              [IntType],
                              [IntType, IntType])
    return


##  RawInputFunc
##
class RawInputFunc(BuiltinConstFunc):

  def __init__(self):
    BuiltinConstFunc.__init__(self, 'raw_input', StrType.get_object(), [StrType])
    return


##  ReduceFunc
##
class ReduceFunc(BuiltinFuncNoKwd):

  class ReduceCaller(CompoundTypeNode):
    
    def __init__(self, frame, anchor, func, seq, initial):
      self.frame = frame
      self.anchor = anchor
      self.received = set()
      self.elem = IterElement(frame, anchor, seq)
      self.result = CompoundTypeNode()
      if initial:
        initial.connect(self.result.recv)
      else:
        self.elem.connect(self.result.recv)
      self.args = (self.result, self.elem)
      CompoundTypeNode.__init__(self, [self.result])
      func.connect(self.recv_func)
      return

    def recv_func(self, src):
      for obj in src:
        if obj in self.received: continue
        self.received.add(obj)
        try:
          result = obj.call(self.frame, self.anchor, self.args, {})
          result.connect(self.recv)
          result.connect(self.result.recv)
        except NodeTypeError:
          self.frame.raise_expt(ErrorConfig.NotCallable(obj))
      return
      
  def __init__(self):
    BuiltinFunc.__init__(self, 'reduce', [ANY, ANY], [ANY])
    return

  def process_args_nokwd(self, frame, anchor, args):
    initial = None
    if 3 <= len(args):
      initial = args[2]
    return self.ReduceCaller(frame, anchor, args[0], args[1], initial)


##  ReprFunc
##
class ReprFunc(BuiltinConstFunc):

  def __init__(self):
    BuiltinConstFunc.__init__(self, 'repr', StrType.get_object(), [ANY])
    return


##  RoundFunc
##
class RoundFunc(BuiltinConstFunc):

  def __init__(self):
    BuiltinConstFunc.__init__(self, 'round', FloatType.get_object(),
                              [NumberType],
                              [IntType])
    return


##  SortedFunc
##
class SortedFunc(BuiltinFunc):

  def __init__(self):
    BuiltinFunc.__init__(self, 'sorted', [ANY])
    return

  def process_args(self, frame, anchor, args, kwargs):
    seq = ListType.create_list(elemall=IterElement(frame, anchor, args[0]))
    ListObject.SortMethod('sorted', seq).process_args(frame, anchor, args[1:], kwargs)
    return seq


##  SumFunc
##
class SumFunc(BuiltinFuncNoKwd):

  class SumCaller(CompoundTypeNode):
    
    def __init__(self, frame, anchor, seq, initial):
      self.frame = frame
      self.anchor = anchor
      self.received = set()
      self.elem = IterElement(frame, anchor, seq)
      self.result = CompoundTypeNode()
      if initial:
        initial.connect(self.result.recv)
      else:
        self.elem.connect(self.result.recv)
      CompoundTypeNode.__init__(self, [self.result])
      IterElement(frame, anchor, seq).connect(self.recv_elem)
      return

    def recv_elem(self, src):
      for obj in src:
        if obj in self.received: continue
        self.received.add(obj)
        BinaryOp(self.frame, self.anchor, 'Add', obj, self.result).connect(self.result.recv)
      return
  
  def __init__(self):
    BuiltinFunc.__init__(self, 'sum', [ANY], [ANY])
    return

  def process_args_nokwd(self, frame, anchor, args):
    initial = None
    if 2 <= len(args):
      initial = args[1]
    return self.SumCaller(frame, anchor, args[0], initial)


##  UnichrFunc
##
class UnichrFunc(BuiltinConstFunc):

  def __init__(self):
    BuiltinConstFunc.__init__(self, 'unichr', UnicodeType.get_object(),
                              [IntType])
    return


##  ZipFunc
##
class ZipFunc(BuiltinFunc):

  def __init__(self):
    BuiltinFunc.__init__(self, 'zip')
    return

  def call(self, frame, anchor, args, kwargs):
    if kwargs:
      frame.raise_expt(ErrorConfig.NoKeywordArgs())
      return UndefinedTypeNode.get_object()
    elems = [ CompoundTypeNode() for arg1 in args ]
    zipelem = TupleType.create_tuple(elements=elems)
    seq = ListType.create_list(elemall=zipelem)
    for (i,arg1) in enumerate(args):
      IterElement(frame, anchor, arg1).connect(elems[i].recv)
    return seq
