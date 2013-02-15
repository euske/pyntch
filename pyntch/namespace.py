#!/usr/bin/env python

from compiler import ast
from pyntch.typenode import CompoundTypeNode, TypeChecker


##  Variable
##
class Variable(CompoundTypeNode):

  def __init__(self, space, name):
    self.space = space
    self.name = name
    CompoundTypeNode.__init__(self)
    return
  
  def __repr__(self):
    return '@'+self.name

  def bind(self, obj):
    obj.connect(self.recv)
    return


##  TypedVariable
##
class TypedVariable(Variable, TypeChecker):
  
  def __init__(self, space, name):
    Variable.__init__(self, space, name)
    return

  def setup(self, frame, validtypes, blame=None):
    TypeChecker.__init__(self, frame, validtypes, blame or repr(self))
    return
  


##  Namespace
##
class Namespace(object):

  def __init__(self, parent_space, name):
    self.parent_space = parent_space
    self.all_names = None
    self.name = name
    self.vars = {}
    if parent_space:
      self.global_space = parent_space.global_space
    else:
      self.global_space = self
    return
  
  def __repr__(self):
    return '<Namespace: %s>' % self.name

  def __contains__(self, name):
    return name in self.vars
  
  def __getitem__(self, name):
    return self.get_var(name)

  def __iter__(self):
    return self.vars.iteritems()

  def get_name(self):
    if self.parent_space:
      return self.parent_space.get_name()+'.'+self.name
    else:
      return self.name

  def get_var(self, name):
    while self:
      if name in self.vars:
        return self.vars[name]
      self = self.parent_space
    raise KeyError(name)

  def register_var(self, name):
    if name not in self.vars:
      var = Variable(self, name)
      self.vars[name] = var
    else:
      var = self.vars[name]
    return var
  
  def register_typed_var(self, name):
    var = TypedVariable(self, name)
    self.vars[name] = var
    return

  # register_names
  def register_names(self, tree):
    from pyntch.module import ModuleNotFound
    from pyntch.config import ErrorConfig

    if isinstance(tree, ast.Module):
      self.register_names(tree.node)
      
    # global
    elif isinstance(tree, ast.Global):
      for name in tree.names:
        self.vars[name] = self.global_space.register_var(name)

    # def
    elif isinstance(tree, ast.Function):
      self.register_var(tree.name)
      for value in tree.defaults:
        self.register_names(value)
    # class
    elif isinstance(tree, ast.Class):
      self.register_var(tree.name)
      for base in tree.bases:
        self.register_names(base)
    # assign
    elif isinstance(tree, ast.Assign):
      for node in tree.nodes:
        self.register_names(tree.expr)
        self.register_names(node)
    elif isinstance(tree, ast.AugAssign):
      self.register_names(tree.expr)
    elif isinstance(tree, ast.AssTuple):
      for c in tree.nodes:
        self.register_names(c)
    elif isinstance(tree, ast.AssList):
      for c in tree.nodes:
        self.register_names(c)
    elif isinstance(tree, ast.AssName):
      self.register_var(tree.name)
    elif isinstance(tree, ast.AssAttr):
      pass
    elif isinstance(tree, ast.Subscript):
      self.register_names(tree.expr)
      for sub in tree.subs:
        self.register_names(sub)

    # return
    elif isinstance(tree, ast.Return):
      self.register_names(tree.value)

    # yield (for both python 2.4 and 2.5)
    elif isinstance(tree, ast.Yield):
      self.register_names(tree.value)

    # with (for __future__ python 2.5 or 2.6)
    elif isinstance(tree, ast.With):
      self.register_names(tree.expr)
      self.register_names(tree.vars)
      self.register_names(tree.body)

    # (mutliple statements)
    elif isinstance(tree, ast.Stmt):
      for stmt in tree.nodes:
        self.register_names(stmt)

    # if, elif, else
    elif isinstance(tree, ast.If):
      for (expr,stmt) in tree.tests:
        self.register_names(expr)
        self.register_names(stmt)
      if tree.else_:
        self.register_names(tree.else_)

    # for
    elif isinstance(tree, ast.For):
      self.register_names(tree.list)
      self.register_names(tree.assign)
      self.register_names(tree.body)
      if tree.else_:
        self.register_names(tree.else_)

    # while
    elif isinstance(tree, ast.While):
      self.register_names(tree.test)
      self.register_names(tree.body)
      if tree.else_:
        self.register_names(tree.else_)

    # try ... except
    elif isinstance(tree, ast.TryExcept):
      self.register_names(tree.body)
      for (expr,e,stmt) in tree.handlers:
        if expr:
          self.register_names(expr)
        if e:
          self.register_names(e)
        self.register_names(stmt)
      if tree.else_:
        self.register_names(tree.else_)

    # try ... finally
    elif isinstance(tree, ast.TryFinally):
      self.register_names(tree.body)
      self.register_names(tree.final)

    # raise
    elif isinstance(tree, ast.Raise):
      if tree.expr1:
        self.register_names(tree.expr1)
      if tree.expr2:
        self.register_names(tree.expr2)
        
    # import
    elif isinstance(tree, ast.Import):
      for (name,asname) in tree.names:
        if asname:
          self.register_var(asname)
        else:
          name = name.split('.')[0]
          self.register_var(name)

    # from
    elif isinstance(tree, ast.From):
      for (name,asname) in tree.names:
        if name == '*':
          modname = tree.modname
          try:
            module = tree._module.load_module(modname)[-1]
            self.import_all(module.space)
          except ModuleNotFound, e:
            ErrorConfig.module_not_found(e.name)
        else:
          self.register_var(asname or name)

    # print, printnl
    elif isinstance(tree, (ast.Print, ast.Printnl)):
      for node in tree.nodes:
        self.register_names(node)
    
    # discard
    elif isinstance(tree, ast.Discard):
      self.register_names(tree.expr)

    # other statements
    elif isinstance(tree, ast.Break):
      pass
    elif isinstance(tree, ast.Continue):
      pass
    elif isinstance(tree, ast.Print):
      pass
    elif isinstance(tree, ast.Yield):
      pass
    elif isinstance(tree, ast.Pass):
      pass
    elif isinstance(tree, ast.Exec):
      pass

    # expressions
    elif isinstance(tree, ast.Const):
      pass
    elif isinstance(tree, ast.Name):
      pass
    elif isinstance(tree, ast.CallFunc):
      self.register_names(tree.node)
      for arg1 in tree.args:
        self.register_names(arg1)
      if tree.star_args:
        self.register_names(tree.star_args)
      if tree.dstar_args:
        self.register_names(tree.dstar_args)
    elif isinstance(tree, ast.Keyword):
      self.register_names(tree.expr)
    elif isinstance(tree, ast.Getattr):
      self.register_names(tree.expr)
    elif isinstance(tree, ast.Slice):      
      self.register_names(tree.expr)
      if tree.lower:
        self.register_names(tree.lower)
      if tree.upper:
        self.register_names(tree.upper)
    elif isinstance(tree, ast.Sliceobj):
      for node in tree.nodes:
        self.register_names(node)
    elif isinstance(tree, ast.Tuple):
      for node in tree.nodes:
        self.register_names(node)
    elif isinstance(tree, ast.List):
      for node in tree.nodes:
        self.register_names(node)
    elif isinstance(tree, ast.Dict):
      for (k,v) in tree.items:
        self.register_names(k)
        self.register_names(v)
    elif isinstance(tree, (ast.Add, ast.Sub, ast.Mul, ast.Div,
                           ast.Mod, ast.FloorDiv, ast.Power,
                           ast.LeftShift, ast.RightShift)):
      self.register_names(tree.left)
      self.register_names(tree.right)
    elif isinstance(tree, ast.Compare):
      self.register_names(tree.expr)
      for (_,node) in tree.ops:
        self.register_names(node)
    elif isinstance(tree, (ast.UnaryAdd, ast.UnarySub, ast.Invert)):
      self.register_names(tree.expr)
    elif isinstance(tree, (ast.And, ast.Or,
                           ast.Bitand, ast.Bitor, ast.Bitxor)):
      for node in tree.nodes:
        self.register_names(node)
    elif isinstance(tree, ast.Not):
      self.register_names(tree.expr)
    elif isinstance(tree, ast.Lambda):
      for value in tree.defaults:
        self.register_names(value)
      self.register_names(tree.code)
    elif isinstance(tree, ast.IfExp):
      self.register_names(tree.test)
      self.register_names(tree.then)
      self.register_names(tree.else_)
    elif isinstance(tree, ast.Backquote):
      self.register_names(tree.expr)

    # list comprehension
    elif isinstance(tree, ast.ListComp):
      self.register_names(tree.expr)
      for qual in tree.quals:
        self.register_names(qual.list)
        self.register_names(qual.assign)
        for qif in qual.ifs:
          self.register_names(qif.test)
    
    # generator expression
    elif isinstance(tree, ast.GenExpr):
      gen = tree.code
      self.register_names(gen.expr)
      for qual in gen.quals:
        self.register_names(qual.iter)
        self.register_names(qual.assign)
        for qif in qual.ifs:
          self.register_names(qif.test)

    # Assert
    elif isinstance(tree, ast.Assert):
      self.register_names(tree.test)
      if tree.fail:
        self.register_names(tree.fail)
      if isinstance(tree.test, ast.CallFunc):
        tests = [ tree.test ]
      else:
        tests = []
      for test in tests:
        if (isinstance(test, ast.CallFunc) and
            isinstance(test.node, ast.Name) and
            test.node.name == 'isinstance' and
            len(test.args) == 2):
          (a,b) = test.args
          if isinstance(a, ast.Name):
            self.register_typed_var(a.name)
    
    # Ellipsis
    elif isinstance(tree, ast.Ellipsis):
      pass
    
    else:
      raise SyntaxError('unsupported syntax: %r (%s:%r)' % (tree, tree._module.get_path(), tree.lineno))
    return

  def register_names_top(self, tree):
    self.register_names(tree)
    if not isinstance(tree, ast.Module): return
    # find '__all__' property
    node = tree.node
    if isinstance(node, ast.Stmt):
      nodes = node.nodes
    else:
      nodes = [node]
    for node in nodes:
      if not isinstance(node, ast.Assign): continue
      if not isinstance(node.expr, ast.List): continue
      for n in node.nodes:
        if isinstance(n, ast.AssName) and n.name == '__all__':
          self.all_names = [ n.value for n in node.expr.nodes
                             if isinstance(n, ast.Const) and isinstance(n.value, str) ]
    return

  def import_all(self, space):
    from pyntch.config import ErrorConfig
    if space.all_names:
      names = space.all_names
    else:
      names = [ k for k in space.vars.iterkeys() if not k.startswith('_') ]
    for k in names:
      try:
        self.vars[k] = space.vars[k]
      except KeyError:
        ErrorConfig.module_not_found(k)
    return


##  BuiltinNamespace
##
class BuiltinTypesNamespace(Namespace):
  
  def __init__(self, parent):
    from pyntch import klass, function, basic_types, aggregate_types, builtin_funcs, module
    Namespace.__init__(self, parent, 'types')
    # types
    self.register_var('type').bind(basic_types.TypeType.get_typeobj())
    self.register_var('NoneType').bind(basic_types.NoneType.get_typeobj())
    self.register_var('int').bind(basic_types.IntType.get_typeobj())
    self.register_var('long').bind(basic_types.LongType.get_typeobj())
    self.register_var('float').bind(basic_types.FloatType.get_typeobj())
    self.register_var('complex').bind(basic_types.ComplexType.get_typeobj())
    self.register_var('bool').bind(basic_types.BoolType.get_typeobj())
    self.register_var('basestring').bind(basic_types.BaseStringType.get_typeobj())
    self.register_var('str').bind(basic_types.StrType.get_typeobj())
    self.register_var('unicode').bind(basic_types.UnicodeType.get_typeobj())
    self.register_var('object').bind(basic_types.ObjectType.get_typeobj())
    self.register_var('file').bind(basic_types.FileType.get_typeobj())
    self.register_var('open').bind(basic_types.FileType.get_typeobj())
    self.register_var('xrange').bind(basic_types.XRangeType.get_typeobj())
    self.register_var('staticmethod').bind(basic_types.StaticMethodType.get_typeobj())
    self.register_var('classmethod').bind(basic_types.ClassMethodType.get_typeobj())
    self.register_var('list').bind(aggregate_types.ListType.get_typeobj())
    self.register_var('tuple').bind(aggregate_types.TupleType.get_typeobj())
    self.register_var('frozenset').bind(aggregate_types.FrozenSetType.get_typeobj())
    self.register_var('set').bind(aggregate_types.SetType.get_typeobj())
    self.register_var('dict').bind(aggregate_types.DictType.get_typeobj())
    self.register_var('enumerate').bind(aggregate_types.EnumerateType.get_typeobj())
    self.register_var('reversed').bind(aggregate_types.ReversedType.get_typeobj())
    
    self.register_var('InstanceType').bind(klass.InstanceType.get_typeobj())
    self.register_var('ModuleType').bind(module.ModuleType.get_typeobj())
    #self.register_var('BuiltinFunctionType').bind(builtin_funcs.BuiltinFunc.get_typeobj())
    #self.register_var('BuiltinMethodType').bind(builtin_funcs.BuiltinFunc.get_typeobj())
    #self.register_var('ClassType').bind(klass.ClassType.get_typeobj())
    #self.register_var('FunctionType').bind(function.FuncType.get_typeobj())
    #self.register_var('LambdaType').bind(function.LambdaFuncType.get_typeobj())
    #self.register_var('GeneratorType').bind(function.IterType.get_typeobj())
    #self.register_var('MethodType').bind(function.MethodType.get_typeobj())

    # obsolete
    #self.register_var('buffer').bind(basic_types.BufferType.get_typeobj())
    #self.register_var('property').bind(basic_types.PropertyType.get_typeobj())
    return
  
class BuiltinExceptionsNamespace(Namespace):
  
  def __init__(self, parent):
    from pyntch import exception
    Namespace.__init__(self, parent, 'exceptions')
    # exceptions
    self.register_var('Exception').bind(exception.ExceptionType.get_typeobj())
    self.register_var('KeyboardInterrupt').bind(exception.KeyboardInterruptType.get_typeobj())
    self.register_var('StopIteration').bind(exception.StopIterationType.get_typeobj())
    self.register_var('StandardError').bind(exception.StandardErrorType.get_typeobj())
    self.register_var('ArithmeticError').bind(exception.ArithmeticErrorType.get_typeobj())
    self.register_var('FloatingPointError').bind(exception.FloatingPointErrorType.get_typeobj())
    self.register_var('OverflowError').bind(exception.OverflowErrorType.get_typeobj())
    self.register_var('ZeroDivisionError').bind(exception.ZeroDivisionErrorType.get_typeobj())
    self.register_var('AssertionError').bind(exception.AssertionErrorType.get_typeobj())
    self.register_var('AttributeError').bind(exception.AttributeErrorType.get_typeobj())
    self.register_var('EnvironmentError').bind(exception.EnvironmentErrorType.get_typeobj())
    self.register_var('IOError').bind(exception.IOErrorType.get_typeobj())
    self.register_var('OSError').bind(exception.OSErrorType.get_typeobj())
    self.register_var('WindowsError').bind(exception.WindowsErrorType.get_typeobj())
    self.register_var('VMSError').bind(exception.VMSErrorType.get_typeobj())
    self.register_var('EOFError').bind(exception.EOFErrorType.get_typeobj())
    self.register_var('ImportError').bind(exception.ImportErrorType.get_typeobj())
    self.register_var('LookupError').bind(exception.LookupErrorType.get_typeobj())
    self.register_var('IndexError').bind(exception.IndexErrorType.get_typeobj())
    self.register_var('KeyError').bind(exception.KeyErrorType.get_typeobj())
    self.register_var('MemoryError').bind(exception.MemoryErrorType.get_typeobj())
    self.register_var('NameError').bind(exception.NameErrorType.get_typeobj())
    self.register_var('UnboundLocalError').bind(exception.UnboundLocalErrorType.get_typeobj())
    self.register_var('ReferenceError').bind(exception.ReferenceErrorType.get_typeobj())
    self.register_var('RuntimeError').bind(exception.RuntimeErrorType.get_typeobj())
    self.register_var('NotImplementedError').bind(exception.NotImplementedErrorType.get_typeobj())
    self.register_var('SyntaxError').bind(exception.SyntaxErrorType.get_typeobj())
    self.register_var('IndentationError').bind(exception.IndentationErrorType.get_typeobj())
    self.register_var('TabError').bind(exception.TabErrorType.get_typeobj())
    self.register_var('SystemError').bind(exception.SystemErrorType.get_typeobj())
    self.register_var('TypeError').bind(exception.TypeErrorType.get_typeobj())
    self.register_var('ValueError').bind(exception.ValueErrorType.get_typeobj())
    self.register_var('UnicodeError').bind(exception.UnicodeErrorType.get_typeobj())
    self.register_var('UnicodeDecodeError').bind(exception.UnicodeDecodeErrorType.get_typeobj())
    self.register_var('UnicodeEncodeError').bind(exception.UnicodeEncodeErrorType.get_typeobj())
    self.register_var('UnicodeTranslateError').bind(exception.UnicodeTranslateErrorType.get_typeobj())
    return
  
class BuiltinNamespace(Namespace):

  def __init__(self, parent):
    from pyntch import basic_types
    from pyntch import builtin_funcs
    Namespace.__init__(self, parent, '__builtin__')
    self.register_var('abs').bind(builtin_funcs.AbsFunc())
    self.register_var('apply').bind(builtin_funcs.ApplyFunc())
    self.register_var('all').bind(builtin_funcs.AllFunc())
    self.register_var('any').bind(builtin_funcs.AnyFunc())
    self.register_var('callable').bind(builtin_funcs.CallableFunc())
    self.register_var('chr').bind(builtin_funcs.ChrFunc())
    self.register_var('cmp').bind(builtin_funcs.CmpFunc())
    self.register_var('dir').bind(builtin_funcs.DirFunc())
    self.register_var('divmod').bind(builtin_funcs.DivmodFunc())
    self.register_var('filter').bind(builtin_funcs.FilterFunc())
    self.register_var('hash').bind(builtin_funcs.HashFunc())
    self.register_var('hex').bind(builtin_funcs.HexFunc())
    self.register_var('id').bind(builtin_funcs.IdFunc())
    self.register_var('isinstance').bind(builtin_funcs.IsInstanceFunc())
    self.register_var('issubclass').bind(builtin_funcs.IsSubclassFunc())
    self.register_var('iter').bind(builtin_funcs.IterFunc())
    self.register_var('len').bind(builtin_funcs.LenFunc())
    self.register_var('map').bind(builtin_funcs.MapFunc())
    self.register_var('max').bind(builtin_funcs.MaxFunc())
    self.register_var('min').bind(builtin_funcs.MinFunc())
    self.register_var('oct').bind(builtin_funcs.OctFunc())
    self.register_var('ord').bind(builtin_funcs.OrdFunc())
    self.register_var('pow').bind(builtin_funcs.PowFunc())
    self.register_var('range').bind(builtin_funcs.RangeFunc())
    self.register_var('raw_input').bind(builtin_funcs.RawInputFunc())
    self.register_var('reduce').bind(builtin_funcs.ReduceFunc())
    self.register_var('repr').bind(builtin_funcs.ReprFunc())
    self.register_var('round').bind(builtin_funcs.RoundFunc())
    self.register_var('sorted').bind(builtin_funcs.SortedFunc())
    self.register_var('sum').bind(builtin_funcs.SumFunc())
    self.register_var('unichr').bind(builtin_funcs.UnichrFunc())
    self.register_var('zip').bind(builtin_funcs.ZipFunc())

    # coerce, intern
    # vars,eval,locals,globals,compile,getattr,hasattr,setattr,delattr,reload,__import__,execfile,input

    # Builtin constants.
    self.register_var('True').bind(basic_types.BoolType.get_object())
    self.register_var('False').bind(basic_types.BoolType.get_object())
    self.register_var('None').bind(basic_types.NoneType.get_object())
    return

class DefaultNamespace(Namespace):
  
  def __init__(self):
    from pyntch import basic_types
    Namespace.__init__(self, None, '(default)')
    self.register_var('__file__').bind(basic_types.StrType.get_object())
    self.register_var('__name__').bind(basic_types.StrType.get_object())
    return

class ModuleNamespace(Namespace):

  def get_name(self):
    return self.name
  
