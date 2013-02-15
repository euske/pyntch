#!/usr/bin/env python

from pyntch.typenode import CompoundTypeNode, \
     NodeTypeError, NodeAttrError, BuiltinType, BuiltinObject, Element
from pyntch.namespace import Namespace, Variable
from pyntch.config import ErrorConfig
from pyntch.module import TreeReporter
from pyntch.frame import ExecutionFrame


# assign_arg(var1,arg1): Assign an argument to a local variable var1.
def assign_arg(frame, anchor, var1, arg1):
  from pyntch.expression import TupleUnpack
  assert not isinstance(var1, list), var1
  assert not isinstance(arg1, list), arg1
  if isinstance(var1, tuple):
    tup = TupleUnpack(frame, anchor, arg1, len(var1))
    for (i,v) in enumerate(var1):
      assign_arg(frame, anchor, v, tup.get_nth(i))
  else:
    var1.bind(arg1)
  return


##  FuncType
##
class FuncType(BuiltinType, TreeReporter):

  TYPE_NAME = 'function'
  
  ##  FuncBody
  ##
  class FuncBody(CompoundTypeNode):

    def __init__(self, name):
      self.name = name
      CompoundTypeNode.__init__(self)
      return

    def __repr__(self):
      return '<funcbody %s>' % self.name

    def set_retval(self, evals):
      from pyntch.aggregate_types import GeneratorType
      returns = [ obj for (t,obj) in evals if t == 'r' ]
      yields = [ obj for (t,obj) in evals if t == 'y' ]
      if yields:
        retvals = [ GeneratorType.create_generator(yields) ]
      else:
        retvals = returns
      for obj in retvals:
        obj.connect(self.recv)
      return

  def __init__(self, parent_reporter, parent_frame, parent_space, anchor,
               name, argnames, defaults, variargs, kwargs, tree):
    TreeReporter.__init__(self, parent_reporter)
    def maprec(func, x):
      if isinstance(x, tuple):
        return tuple( maprec(func, y) for y in x )
      else:
        return func(x)
    self.name = name
    # prepare local variables that hold passed arguments.
    self.space = Namespace(parent_space, name)
    self.frame = ExecutionFrame(None, tree)
    # handle "**kwd".
    self.kwarg = None
    if kwargs:
      self.kwarg = argnames[-1]
      del argnames[-1]
      self.space.register_var(self.kwarg)
    # handle "*args".
    self.variarg = None
    if variargs:
      self.variarg = argnames[-1]
      del argnames[-1]
      self.space.register_var(self.variarg)
    # handle normal args.
    self.argnames = tuple(argnames)
    maprec(lambda argname: self.space.register_var(argname), self.argnames)
    # build the function body.
    self.space.register_names(tree.code)
    self.body = self.FuncBody(name)
    self.body.set_retval(self.build_evals(tree.code))
    self.argvars = maprec(lambda argname: self.space[argname], self.argnames)
    # assign the default values.
    self.defaults = tuple(defaults)
    for (var1,arg1) in zip(self.argvars[-len(defaults):], self.defaults):
      assign_arg(parent_frame, anchor, var1, arg1)
    self.frames = set()
    BuiltinType.__init__(self)
    return

  def build_evals(self, code):
    from pyntch.syntax import build_stmt
    evals = []
    build_stmt(self, self.frame, self.space, code, evals, isfuncdef=True)
    return evals

  def __repr__(self):
    return ('<function %s>' % self.get_name())

  def descxml(self, done):
    done[self] = len(done)
    return Element('function', name=self.get_name())
  
  def get_name(self):
    return self.space.get_name()
  
  def get_type(self):
    return self

  def call(self, frame, anchor, args, kwargs):
    from pyntch.basic_types import StrType
    from pyntch.aggregate_types import DictType, TupleType
    from pyntch.expression import TupleUnpack, TupleSlice
    # Process keyword arguments first.
    varsleft = list(self.argvars)
    varikwargs = []
    for (kwname, kwvalue) in kwargs.iteritems():
      for var1 in varsleft:
        if isinstance(var1, Variable) and var1.name == kwname:
          var1.bind(kwvalue)
          # When a keyword argument is given, remove that name from the remaining arguments.
          varsleft.remove(var1)
          break
      else:
        if self.kwarg:
          varikwargs.append(kwvalue)
        else:
          frame.raise_expt(ErrorConfig.InvalidKeywordArgs(kwname))
    # Process standard arguments.
    variargs = []
    for arg1 in args:
      assert arg1 != None, args
      if varsleft:
        var1 = varsleft.pop(0)
        assign_arg(frame, anchor, var1, arg1)
      elif self.variarg:
        variargs.append(arg1)
      else:
        # Too many arguments.
        frame.raise_expt(ErrorConfig.InvalidNumOfArgs(len(self.argvars), len(args)))
    if len(self.defaults) < len(varsleft):
      # Too few arguments.
      frame.raise_expt(ErrorConfig.InvalidNumOfArgs(len(self.argvars), len(args)))
    # Handle remaining arguments: kwargs and variargs.
    if self.variarg and variargs:
      self.space[self.variarg].bind(TupleType.create_tuple(variargs))
    if self.kwarg:
      if varikwargs:
        self.space[self.kwarg].bind(DictType.create_dict(key=StrType.get_object(), value=varikwargs))
      else:
        self.space[self.kwarg].bind(DictType.create_null(frame, anchor))
    # Remember where this is called from.
    self.frames.add(frame)
    # Propagate the exceptions upward.
    self.frame.connect(frame.recv)
    return self.body

  def showtxt(self, out):
    (module,lineno) = self.frame.getloc()
    out.write('### %s(%s)' % (module.get_name(), lineno))
    for frame in self.frames:
      (module,lineno) = frame.getloc()
      out.write('# called at %s(%s)' % (module.get_name(), lineno))
    names = set()
    def recjoin(sep, seq):
      for x in seq:
        if isinstance(x, tuple):
          yield '(%s)' % sep.join(recjoin(sep, x))
        else:
          names.add(x)
          yield '%s=%s' % (x, self.space[x].desctxt({}))
      return
    r = list(recjoin(', ', self.argnames))
    if self.variarg:
      r.append('*'+self.variarg)
    if self.kwarg:
      r.append('**'+self.kwarg)
    out.write('def %s(%s):' % (self.name, ', '.join(r)) )
    out.indent(+1)
    names.update( child.name for child in self.children )
    for (k,v) in sorted(self.space):
      if k not in names:
        out.write_value(k, v)
    out.write_value('return', self.body)
    self.frame.showtxt(out)
    for child in self.children:
      child.showtxt(out)
    out.indent(-1)
    out.write('')
    return

  def showxml(self, out):
    (module,lineno) = self.frame.getloc()
    out.start_xmltag('function', name=self.name)
    for frame in self.frames:
      (module,lineno) = frame.getloc()
      out.show_xmltag('caller', loc='%s:%s' % (module.get_name(), lineno))
    names = set()
    def recjoin(seq):
      for x in seq:
        if isinstance(x, tuple):
          recjoin(x)
        else:
          names.add(x)
          out.show_xmlvalue('arg', self.space[x], name=x)
      return
    recjoin(self.argnames)
    if self.variarg:
      out.show_xmltag('vararg', name=self.variarg)
    if self.kwarg:
      out.show_xmltag('kwarg', name=self.kwarg)
    names.update( child.name for child in self.children )
    for (k,v) in sorted(self.space):
      if k not in names:
        out.show_xmlvalue('var', v, name=k)
    out.show_xmlvalue('return', self.body)
    self.frame.showxml(out)
    for child in self.children:
      child.showxml(out)
    out.end_xmltag('function')
    return


class StaticMethodType(FuncType): pass
class ClassMethodType(FuncType): pass


##  LambdaFuncType
##
class LambdaFuncType(FuncType):
  
  def __init__(self, parent_reporter, parent_frame, parent_space, anchor,
               argnames, defaults, variargs, kwargs, tree):
    name = '__lambda_%x' % id(tree)
    FuncType.__init__(self, parent_reporter, parent_frame, parent_space, anchor,
                      name, argnames, defaults, variargs, kwargs, tree)
    return

  def build_evals(self, code):
    from pyntch.syntax import build_expr
    evals = []
    evals.append( ('r', build_expr(self, self.frame, self.space, code, evals)) )
    return evals
  
  def __repr__(self):
    return ('<lambda %s>' % self.name)
