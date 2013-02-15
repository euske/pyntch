#!/usr/bin/env python

from compiler import ast
from pyntch.typenode import TypeNode, UndefinedTypeNode, CompoundTypeNode, TypeChecker
from pyntch.frame import ExecutionFrame, ExceptionCatcher, ExceptionMaker
from pyntch.config import ErrorConfig
from pyntch.klass import PythonClassType
from pyntch.function import FuncType, LambdaFuncType
from pyntch.expression import ExpressionNode, AttrRef, SubRef, SliceRef, \
     AttrAssign, SubAssign, SliceAssign, \
     FunCall, BinaryOp, UnaryOp, AssignOp, CompareOp, BooleanOp, NotOp, IfExpOp, \
     IterElement, TupleUnpack


##  SliceObject
##
class SliceObject(ExpressionNode):
  
  def __init__(self, frame, anchor, nodes):
    self.nodes = nodes
    ExpressionNode.__init__(self, frame, anchor)
    return


##  build_assert(reporter, frame, space, tree, arg, evals)
##
def build_assert(reporter, frame, space, tree, arg, evals):
  # "assert isinstance() and isinstance() and ...
  if isinstance(tree, ast.CallFunc):
    tests = [ tree ]
  else:
    return
  for node in tests:
    if (isinstance(node, ast.CallFunc) and
        isinstance(node.node, ast.Name) and
        node.node.name == 'isinstance' and
        len(node.args) == 2):
      (a,b) = node.args
      if isinstance(b, ast.Tuple):
        b = b.nodes
      else:
        b = [b]
      validtypes = [ build_expr(reporter, frame, space, t, evals) for t in b ]
      if isinstance(a, ast.Name):
        checker = space[a.name]
        checker.setup(frame, validtypes, arg)
      elif arg and isinstance(arg, ast.Const):
        checker = TypeChecker(frame, validtypes, arg.value)
      else:
        checker = TypeChecker(frame, validtypes, repr(a))
      build_expr(reporter, frame, space, a, evals).connect(checker.recv)
  return


##  build_assign(reporter, frame, namespace, node1, node2, evals)
##
def build_assign(reporter, frame, space, n, v, evals):
  if isinstance(n, ast.AssName) or isinstance(n, ast.Name):
    space[n.name].bind(v)
  elif isinstance(n, ast.AssTuple) or isinstance(n, ast.AssList):
    tup = TupleUnpack(ExecutionFrame(frame, n), n, v, len(n.nodes))
    for (i,c) in enumerate(n.nodes):
      build_assign(reporter, frame, space, c, tup.get_nth(i), evals)
  elif isinstance(n, (ast.AssAttr, ast.Getattr)):
    obj = build_expr(reporter, frame, space, n.expr, evals)
    AttrAssign(ExecutionFrame(frame, n), n, obj, n.attrname, v)
  elif isinstance(n, ast.Subscript):
    obj = build_expr(reporter, frame, space, n.expr, evals)
    subs = [ build_expr(reporter, frame, space, expr, evals) for expr in n.subs ]
    if len(subs) == 1:
      SubAssign(ExecutionFrame(frame, n), n, obj, subs[0], v)
    else:
      SliceAssign(ExecutionFrame(frame, n), n, obj, subs, v)
  elif isinstance(n, ast.Slice):
    obj = build_expr(reporter, frame, space, n.expr, evals)
    lower = upper = None
    if n.lower:
      lower = build_expr(reporter, frame, space, n.lower, evals)
    if n.upper:
      upper = build_expr(reporter, frame, space, n.upper, evals)
    SliceAssign(ExecutionFrame(frame, n), n, obj, [lower, upper], v)
  else:
    raise SyntaxError('unsupported syntax: %r (%s:%r)' % (n, n._module.get_path(), n.lineno))
  return


##  build_expr(reporter, frame, namespace, tree, evals)
##
##  Constructs a TypeNode from a given syntax tree.
##
def build_expr(reporter, frame, space, tree, evals):
  from pyntch.basic_types import BUILTIN_OBJECT, IntType
  from pyntch.aggregate_types import IterType, GeneratorType, ListType, DictType, TupleType

  if isinstance(tree, ast.Const):
    typename = type(tree.value).__name__
    expr = BUILTIN_OBJECT[typename]

  elif isinstance(tree, ast.Name):
    try:
      expr = space[tree.name]
    except KeyError:
      ExecutionFrame(frame, tree).raise_expt(ErrorConfig.NameUndefined(tree.name))
      expr = UndefinedTypeNode(tree.name)

  elif isinstance(tree, ast.CallFunc):
    func = build_expr(reporter, frame, space, tree.node, evals)
    args = tuple( build_expr(reporter, frame, space, arg1, evals)
                  for arg1 in tree.args if not isinstance(arg1, ast.Keyword) )
    kwargs = dict( (arg1.name, build_expr(reporter, frame, space, arg1.expr, evals))
                   for arg1 in tree.args if isinstance(arg1, ast.Keyword) )
    star = dstar = None
    if tree.star_args:
      star = build_expr(reporter, frame, space, tree.star_args, evals)
    if tree.dstar_args:
      dstar = build_expr(reporter, frame, space, tree.dstar_args, evals)
    expr = FunCall(ExecutionFrame(frame, tree), tree, func, args, kwargs, star, dstar)

  elif isinstance(tree, ast.Getattr):
    obj = build_expr(reporter, frame, space, tree.expr, evals)
    expr = AttrRef(ExecutionFrame(frame, tree), tree, obj, tree.attrname)

  elif isinstance(tree, ast.Subscript):
    obj = build_expr(reporter, frame, space, tree.expr, evals)
    subs = [ build_expr(reporter, frame, space, sub, evals) for sub in tree.subs ]
    if len(subs) == 1:
      expr = SubRef(ExecutionFrame(frame, tree), tree, obj, subs[0])
    else:
      expr = SliceRef(ExecutionFrame(frame, tree), tree, obj, subs)
      
  elif isinstance(tree, ast.Slice):
    obj = build_expr(reporter, frame, space, tree.expr, evals)
    lower = upper = IntType.get_object() # maxint is given when omitted.
    if tree.lower:
      lower = build_expr(reporter, frame, space, tree.lower, evals)
    if tree.upper:
      upper = build_expr(reporter, frame, space, tree.upper, evals)
    assert lower != None and upper != None
    expr = SliceRef(ExecutionFrame(frame, tree), tree, obj, [lower, upper])

  elif isinstance(tree, ast.Sliceobj):
    elements = [ build_expr(reporter, frame, space, node, evals) for node in tree.nodes ]
    expr = SliceObject(ExecutionFrame(frame, tree), tree, elements)
    
  elif isinstance(tree, ast.Tuple):
    elements = [ build_expr(reporter, frame, space, node, evals) for node in tree.nodes ]
    expr = TupleType.create_tuple(elements)

  elif isinstance(tree, ast.List):
    elements = [ build_expr(reporter, frame, space, node, evals) for node in tree.nodes ]
    expr = ListType.create_list(CompoundTypeNode(elements))

  elif isinstance(tree, ast.Dict):
    items = [ (build_expr(reporter, frame, space, k, evals),
               build_expr(reporter, frame, space, v, evals))
              for (k,v) in tree.items ]
    expr = DictType.create_dict(items)

  # +, -, *, /, %, //, **, <<, >>
  elif isinstance(tree, (ast.Add, ast.Sub, ast.Mul, ast.Div,
                         ast.Mod, ast.FloorDiv, ast.Power,
                         ast.LeftShift, ast.RightShift)):
    op = tree.__class__.__name__
    left = build_expr(reporter, frame, space, tree.left, evals)
    right = build_expr(reporter, frame, space, tree.right, evals)
    expr = BinaryOp(ExecutionFrame(frame, tree), tree, op, left, right)
    
  # &, |, ^
  elif isinstance(tree, (ast.Bitand, ast.Bitor, ast.Bitxor)):
    op = tree.__class__.__name__
    nodes = [ build_expr(reporter, frame, space, node, evals) for node in tree.nodes ]
    expr = nodes.pop(0)
    for right in nodes:
      expr = BinaryOp(ExecutionFrame(frame, tree), tree, op, expr, right)
  
  # ==, !=, <=, >=, <, >, in, not in, is, is not
  elif isinstance(tree, ast.Compare):
    left = build_expr(reporter, frame, space, tree.expr, evals)
    for (op,node) in tree.ops:
      right = build_expr(reporter, frame, space, node, evals)
      expr = CompareOp(ExecutionFrame(frame, tree), tree, op, left, right)
      left = right

  # +,-,~
  elif isinstance(tree, (ast.UnaryAdd, ast.UnarySub, ast.Invert)):
    op = tree.__class__.__name__
    value = build_expr(reporter, frame, space, tree.expr, evals)
    expr = UnaryOp(ExecutionFrame(frame, tree), tree, op, value)

  # and, or
  elif isinstance(tree, (ast.And, ast.Or)):
    op = tree.__class__.__name__
    nodes = [ build_expr(reporter, frame, space, node, evals) for node in tree.nodes ]
    expr = BooleanOp(ExecutionFrame(frame, tree), tree, op, nodes)

  # not
  elif isinstance(tree, ast.Not):
    value = build_expr(reporter, frame, space, tree.expr, evals)
    expr = NotOp(ExecutionFrame(frame, tree), tree, value)

  # lambda
  elif isinstance(tree, ast.Lambda):
    defaults = [ build_expr(reporter, frame, space, value, evals) for value in tree.defaults ]
    expr = LambdaFuncType(reporter, frame, space, tree, tree.argnames,
                          defaults, tree.varargs, tree.kwargs, tree)

  # list comprehension
  elif isinstance(tree, ast.ListComp):
    elements = [ build_expr(reporter, frame, space, tree.expr, evals) ]
    expr = ListType.create_list(CompoundTypeNode(elements))
    for qual in tree.quals:
      seq = build_expr(reporter, frame, space, qual.list, evals)
      elem = IterElement(ExecutionFrame(frame, qual.list), qual.list, seq)
      build_assign(reporter, frame, space, qual.assign, elem, evals)
      for qif in qual.ifs:
        build_expr(reporter, frame, space, qif.test, evals)

  # generator expression
  elif isinstance(tree, ast.GenExpr):
    gen = tree.code
    elements = [ build_expr(reporter, frame, space, gen.expr, evals) ]
    expr = IterType.create_iter(CompoundTypeNode(elements))
    for qual in gen.quals:
      seq = build_expr(reporter, frame, space, qual.iter, evals)
      elem = IterElement(ExecutionFrame(frame, qual.iter), qual.iter, seq)
      build_assign(reporter, frame, space, qual.assign, elem, evals)
      for qif in qual.ifs:
        build_expr(reporter, frame, space, qif.test, evals)

  # yield (for python 2.5)
  elif isinstance(tree, ast.Yield):
    value = build_expr(reporter, frame, space, tree.value, evals)
    slot = GeneratorType.create_slot(value)
    evals.append(('y', slot))
    expr = slot.received

  # ifexp
  elif isinstance(tree, ast.IfExp):
    test = build_expr(reporter, frame, space, tree.test, evals)
    then = build_expr(reporter, frame, space, tree.then, evals)
    else_ = build_expr(reporter, frame, space, tree.else_, evals)
    expr = IfExpOp(ExecutionFrame(frame, tree), tree, test, then, else_)

  # Backquote (unsupported)
  elif isinstance(tree, ast.Backquote):
    ExecutionFrame(frame, tree).raise_expt(ErrorConfig.NotSupported('backquote notation'))
    expr = UndefinedTypeNode('backquote')

  # Ellipsis
  elif isinstance(tree, ast.Ellipsis):
    ExecutionFrame(frame, tree).raise_expt(ErrorConfig.NotSupported('ellipsis'))
    expr = UndefinedTypeNode('ellipsis')
  
  else:
    # unsupported AST.
    raise SyntaxError('unsupported syntax: %r (%s:%r)' % (tree, tree._module.get_path(), tree.lineno))

  assert isinstance(expr, (TypeNode, tuple)), expr
  evals.append((None, expr))
  return expr


##  build_stmt
##
def build_stmt(reporter, frame, space, tree, evals, isfuncdef=False, parent_space=None):
  from pyntch.basic_types import NoneType, StrType
  from pyntch.module import ModuleNotFound
  from pyntch.config import ErrorConfig
  assert isinstance(frame, ExecutionFrame)

  if isinstance(tree, ast.Module):
    build_stmt(reporter, frame, space, tree.node, evals)
  
  # def
  elif isinstance(tree, ast.Function):
    name = tree.name
    defaults = [ build_expr(reporter, frame, space, value, evals) for value in tree.defaults ]
    parent_space = parent_space or space # class definition
    func = FuncType(reporter, frame, parent_space, tree, name, tree.argnames,
                    defaults, tree.varargs, tree.kwargs, tree)
    if tree.decorators:
      for node in tree.decorators:
        decor = build_expr(reporter, frame, space, node, evals)
        func = FunCall(ExecutionFrame(frame, node), node, decor, (func,))
    space[name].bind(func)

  # class
  elif isinstance(tree, ast.Class):
    name = tree.name
    bases = [ build_expr(reporter, frame, space, base, evals) for base in tree.bases ]
    klass = PythonClassType(reporter, frame, space, tree, name, bases, evals, tree)
    space[name].bind(klass)

  # assign
  elif isinstance(tree, ast.Assign):
    for n in tree.nodes:
      value = build_expr(reporter, frame, space, tree.expr, evals)
      build_assign(reporter, frame, space, n, value, evals)

  # augassign
  elif isinstance(tree, ast.AugAssign):
    left = build_expr(reporter, frame, space, tree.node, evals)
    if isinstance(left, UndefinedTypeNode):
      # ignore an undefined variable.
      pass
    else:
      right = build_expr(reporter, frame, space, tree.expr, evals)
      value = AssignOp(ExecutionFrame(frame, tree), tree, tree.op, left, right)
      build_assign(reporter, frame, space, tree.node, value, evals)

  # return
  elif isinstance(tree, ast.Return):
    value = build_expr(reporter, frame, space, tree.value, evals)
    evals.append(('r', value))
    return True

  # yield (for python 2.4)
  elif isinstance(tree, ast.Yield):
    value = build_expr(reporter, frame, space, tree.value, evals)
    evals.append(('y', value))
    return True

  # (mutliple statements)
  elif isinstance(tree, ast.Stmt):
    stmt = None
    exit = False
    for stmt in tree.nodes:
      exit = build_stmt(reporter, frame, space, stmt, evals, parent_space=parent_space)
    if isfuncdef and not exit:
      # if the last statement is not a Return or Raise
      value = NoneType.get_object()
      evals.append(('r', value))
    return exit

  # if, elif, else
  elif isinstance(tree, ast.If):
    for (expr,stmt) in tree.tests:
      value = build_expr(reporter, frame, space, expr, evals)
      exit = build_stmt(reporter, frame, space, stmt, evals)
    if tree.else_:
      exit = build_stmt(reporter, frame, space, tree.else_, evals) and exit
    else:
      exit = False
    return exit

  # for
  elif isinstance(tree, ast.For):
    seq = build_expr(reporter, frame, space, tree.list, evals)
    elem = IterElement(ExecutionFrame(frame, tree.list), tree.list, seq)
    build_assign(reporter, frame, space, tree.assign, elem, evals)
    exit = build_stmt(reporter, frame, space, tree.body, evals)
    if tree.else_:
      exit = build_stmt(reporter, frame, space, tree.else_, evals) and exit
    return exit

  # while
  elif isinstance(tree, ast.While):
    value = build_expr(reporter, frame, space, tree.test, evals)
    exit = build_stmt(reporter, frame, space, tree.body, evals)
    if tree.else_:
      exit = build_stmt(reporter, frame, space, tree.else_, evals) and exit
    return exit

  # try ... except
  elif isinstance(tree, ast.TryExcept):
    catcher = ExceptionCatcher(frame)
    for (expr,e,stmt) in tree.handlers:
      if expr:
        expts = build_expr(reporter, frame, space, expr, evals)
        handler = catcher.add_handler(expts)
        if e:
          build_assign(reporter, handler, space, e, handler.var, evals)
      else:
        handler = catcher.add_handler(None)
      exit = build_stmt(reporter, handler, space, stmt, evals)
    exit = build_stmt(reporter, catcher, space, tree.body, evals) and exit
    if tree.else_:
      exit = build_stmt(reporter, frame, space, tree.else_, evals) and exit
    return exit

  # try ... finally
  elif isinstance(tree, ast.TryFinally):
    exit = build_stmt(reporter, frame, space, tree.body, evals)
    exit = build_stmt(reporter, frame, space, tree.final, evals) and exit
    return exit

  # raise
  elif isinstance(tree, ast.Raise):
    # XXX ignoring tree.expr3 (what is this for anyway?)
    if tree.expr2:
      expttype = build_expr(reporter, frame, space, tree.expr1, evals)
      exptarg = build_expr(reporter, frame, space, tree.expr2, evals)
      ExceptionMaker(ExecutionFrame(frame, tree), tree, expttype, (exptarg,))
    elif tree.expr1:
      expttype = build_expr(reporter, frame, space, tree.expr1, evals)
      ExceptionMaker(ExecutionFrame(frame, tree), tree, expttype, ())
    else:
      # re-raise
      frame.set_reraise()

  # printnl
  elif isinstance(tree, (ast.Print, ast.Printnl)):
    for node in tree.nodes:
      value = build_expr(reporter, frame, space, node, evals)
      StrType.StrConverter(ExecutionFrame(frame, node), tree, value)

  # discard
  elif isinstance(tree, ast.Discard):
    value = build_expr(reporter, frame, space, tree.expr, evals)

  # pass, break, continue
  elif isinstance(tree, (ast.Pass, ast.Break, ast.Continue)):
    pass

  # import
  elif isinstance(tree, ast.Import):
    for (name,asname) in tree.names:
      try:
        modules = tree._module.load_module(name)
        if asname:
          space[asname].bind(modules[-1])
        else:
          asname = name.split('.')[0]
          space[asname].bind(modules[0])
      except ModuleNotFound, e:
        ErrorConfig.module_not_found(e.name)
        
  elif isinstance(tree, ast.From):
    try:
      modname = tree.modname
      modules = tree._module.load_module(modname)
      for (name,asname) in tree.names:
        if name != '*':
          try:
            obj = modules[-1].import_object(name)
            space[asname or name].bind(obj)
          except ModuleNotFound, e:
            ErrorConfig.module_not_found(modname+'.'+e.name)
    except ModuleNotFound, e:
      ErrorConfig.module_not_found(e.name)
  
  # global
  elif isinstance(tree, ast.Global):
    pass

  # with (for __future__ python 2.5 or 2.6)
  elif isinstance(tree, ast.With):
    # XXX need to call __enter__ and __exit__
    value = build_expr(reporter, frame, space, tree.expr, evals)
    build_assign(reporter, frame, space, tree.vars, value, evals)
    build_stmt(reporter, frame, space, tree.body, evals)

  # del
  elif isinstance(tree, ast.AssName):
    pass
  elif isinstance(tree, ast.AssTuple):
    pass
  elif isinstance(tree, ast.AssList):
    pass
  elif isinstance(tree, ast.AssAttr):
    build_expr(reporter, frame, space, tree.expr, evals)
  elif isinstance(tree, ast.Subscript):
    build_expr(reporter, frame, space, tree.expr, evals)
  elif isinstance(tree, ast.Slice):
    assert tree.flags == 'OP_DELETE'
    build_expr(reporter, frame, space, tree.expr, evals)
    if tree.lower:
      build_expr(reporter, frame, space, tree.lower, evals)
    if tree.upper:
      build_expr(reporter, frame, space, tree.upper, evals)

  elif isinstance(tree, ast.Assert):
    frame1 = ExecutionFrame(frame, tree)
    build_assert(reporter, frame1, space, tree.test, tree.fail, evals)
    build_expr(reporter, frame, space, tree.test, evals)
    if tree.fail:
      build_expr(reporter, frame, space, tree.fail, evals)

  # unsupported
  elif isinstance(tree, ast.Exec):
    ExecutionFrame(frame, tree).raise_expt(ErrorConfig.NotSupported('exec'))
  
  else:
    raise SyntaxError('unsupported syntax: %r (%s:%r)' % (tree, tree._module.get_path(), tree.lineno))

  return False
