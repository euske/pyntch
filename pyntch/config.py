#!/usr/bin/env python
import sys
from pyntch.exception import SyntaxErrorType, TypeErrorType, ValueErrorType, \
     AttributeErrorType, IndexErrorType, IOErrorType, EOFErrorType, \
     KeyErrorType, NameErrorType, RuntimeErrorType, OSErrorType, \
     UnicodeDecodeErrorType, UnicodeEncodeErrorType

class ErrorConfig(object):

  raise_uncertain = False
  
  ignore_none = True

  show_all_exceptions = False

  unfound_modules = set()
  
  @classmethod
  def module_not_found(klass, modname):
    klass.unfound_modules.add(modname)
    return
  
  @classmethod
  def is_ignored(klass, obj):
    from pyntch.basic_types import NoneType
    return klass.ignore_none and obj.is_type(NoneType.get_typeobj())

  # occur
  @classmethod
  def RaiseOutsideTry(klass):
    return SyntaxErrorType.occur('raise with no argument outside try-except')
  
  @classmethod
  def NameUndefined(klass, name):
    return NameErrorType.occur('undefined: %s' % name)

  @classmethod
  def NotSupported(klass, name):
    return RuntimeErrorType.occur('not supported feature: %s' % name)
  
  @classmethod
  def NotInstantiatable(klass, typename):
    return TypeErrorType.occur('not instantiatable: %s' % typename)
  
  @classmethod
  def NoKeywordArgs(klass):
    return TypeErrorType.occur('cannot take a keyword argument')
  
  @classmethod
  def NoKeywordArg1(klass, kwd):
    return TypeErrorType.occur('cannot take keyword: %s' % kwd)
  
  @classmethod
  def InvalidKeywordArgs(klass, kwd):
    return TypeErrorType.occur('invalid keyword argument: %s' % kwd)
  
  @classmethod
  def InvalidNumOfArgs(klass, valid, nargs):
    if valid < nargs:
      return TypeErrorType.occur('too many args: %r required, %r given' % (valid, nargs))
    else:
      return TypeErrorType.occur('too few args: %r given, %r required' % (nargs, valid))

  @classmethod
  def NotConvertable(klass, typename):
    return ValueErrorType.occur('not convertable to %s' % typename)

  @classmethod
  def NotCallable(klass, obj):
    if klass.is_ignored(obj): return None
    return TypeErrorType.occur('not callable: %s' % obj)
  
  @classmethod
  def NotIterable(klass, obj):
    if klass.is_ignored(obj): return None
    return TypeErrorType.occur('not iterable: %s' % obj)
  
  @classmethod
  def NotSubscriptable(klass, obj):
    if klass.is_ignored(obj): return None
    return TypeErrorType.occur('not subscriptable: %s' % obj)
  
  @classmethod
  def NotAssignable(klass, obj):
    if klass.is_ignored(obj): return None
    return TypeErrorType.occur('cannot assign item: %s' % obj)
  
  @classmethod
  def NoLength(klass, obj):
    if klass.is_ignored(obj): return None
    return TypeErrorType.occur('length not defined: %s' % obj)
  
  @classmethod
  def AttributeNotFound(klass, obj, attrname):
    if klass.is_ignored(obj): return None
    return AttributeErrorType.occur('attribute not found: %s.%s' % (obj, attrname))
  
  @classmethod
  def AttributeNotAssignable(klass, obj, attrname):
    if klass.is_ignored(obj): return None
    return AttributeErrorType.occur('attribute cannot be assigned: %s.%s' % (obj, attrname))
  
  @classmethod
  def NotUnpackable(klass, obj):
    if klass.is_ignored(obj): return None
    return ValueErrorType.occur('tuple cannot be unpacked: %s' % obj)
  
  @classmethod
  def NotSupportedOperand(klass, op, left, right=None):
    if right:
      if klass.is_ignored(left) or klass.is_ignored(right): return None
      return TypeErrorType.occur('not supported operand %s(%s, %s)' %
                                 (op, left.get_type().typename(), right.get_type().typename()))
    else:
      if klass.is_ignored(left): return None
      return TypeErrorType.occur('not supported operand %s(%s)' % (op, left.get_type().typename()))

  @classmethod
  def TypeCheckerError(klass, src, obj, validtype):
    return TypeErrorType.occur('%s (%s) must be %s' % (src, obj, validtype))

  # maybe
  @classmethod
  def MaybeNotConvertable(klass, typename):
    if not klass.raise_uncertain: return None
    return ValueErrorType.maybe('not convertable to %s' % typename)
  
  @classmethod
  def MaybeOutOfRange(klass):
    if not klass.raise_uncertain: return None
    return IndexErrorType.maybe('index out of range')
  
  @classmethod
  def MaybeKeyNotFound(klass):
    if not klass.raise_uncertain: return None
    return KeyErrorType.maybe('key not found')
  
  @classmethod
  def MaybeElementNotFound(klass):
    if not klass.raise_uncertain: return None
    return ValueErrorType.maybe('element not found')
  
  @classmethod
  def MaybeElementNotRemovable(klass):
    if not klass.raise_uncertain: return None
    return ValueErrorType.maybe('empty container')
  
  @classmethod
  def MaybeNotRemovable(klass):
    if not klass.raise_uncertain: return None
    return ValueErrorType.maybe('cannot remove an entry')
  
  @classmethod
  def MaybeNotDecodable(klass):
    if not klass.raise_uncertain: return None
    return UnicodeDecodeErrorType.maybe('unicode not decodable')
  
  @classmethod
  def MaybeNotEncodable(klass):
    if not klass.raise_uncertain: return None
    return UnicodeEncodeErrorType.maybe('unicode not encodable')
  
  @classmethod
  def MaybeSubstringNotFound(klass):
    if not klass.raise_uncertain: return None
    return ValueErrorType.maybe('substring not found')
  
  @classmethod
  def MaybeTableInvalid(klass):
    if not klass.raise_uncertain: return None
    return ValueErrorType.maybe('translate table invalid')
  
  @classmethod
  def MaybeFileCannotOpen(klass):
    if not klass.raise_uncertain: return None
    return IOErrorType.maybe('cannot open a file')
  
  @classmethod
  def MaybeFileIllegalSeek(klass):
    if not klass.raise_uncertain: return None
    return IOErrorType.maybe('illegal seek')
  
  @classmethod
  def MaybeEOFError(klass):
    if not klass.raise_uncertain: return None
    return EOFErrorType.maybe('end of file')
  
  @classmethod
  def load(klass, fname):
    fp = file(fname, 'r')
    data = fp.read()
    fp.close()
    code = compile(data, fname, 'exec')
    dic = {}
    eval(code, dic)
    for (k,v) in dic.iteritems():
      if k.startswith('_'): continue
      klass.set(k, v)
    return

  @classmethod
  def set(klass, k, v):
    if hasattr(klass, k):
      setattr(klass, k, v)
    else:
      print >>sys.stderr, 'invalid option: ErrorConfig.%s' % k
    return
