#!/usr/bin/env python

from pyntch.typenode import TypeNode, CompoundTypeNode, \
     NodeTypeError, NodeAttrError, NodeAssignError, \
     BuiltinType, BuiltinObject
from pyntch.klass import ClassType, InstanceObject


##  ExceptionType
##
##  ExceptionType is a built-in Python type so it should be
##  defined within the basic_types module, but it's used
##  throughout the entire program so we define it here for a
##  convenience.
##
class InternalException(InstanceObject):

  def __init__(self, klass, message=None):
    self.message = message
    InstanceObject.__init__(self, klass)
    return

  def __repr__(self):
    return '%s: %s' % (self.klass.typename(), self.message)
  
  def typename(self):
    return self.klass.typename()


##  ExceptionType
##
class ExceptionType(ClassType):

  TYPE_NAME = 'Exception'
  OBJECTS = {}

  def __init__(self):
    ClassType.__init__(self, self.TYPE_NAME, [])
    return

  def get_attr(self, frame, anchor, name, write=False):
    if name == '__init__':
      if write: raise NodeAssignError(name)
      return self.InitMethod(self)
    return ClassType.get_attr(self, frame, anchor, name, write=write)

  @classmethod
  def occur(klass, message):
    k = (klass.get_typeobj(), message)
    if k in klass.OBJECTS:
      expt = klass.OBJECTS[k]
    else:
      expt = InternalException(klass.get_typeobj(), message)
      klass.OBJECTS[k] = expt
    return expt
  maybe = occur

class KeyboardInterruptType(ExceptionType):
  TYPE_NAME = 'KeyboardInterrupt'
class StopIterationType(ExceptionType):
  TYPE_NAME = 'StopIteration'
class StandardErrorType(ExceptionType):
  TYPE_NAME = 'StandardError'
class ArithmeticErrorType(StandardErrorType):
  TYPE_NAME = 'ArithmeticError'
class FloatingPointErrorType(ArithmeticErrorType):
  TYPE_NAME = 'FloatingPointError'
class OverflowErrorType(ArithmeticErrorType):
  TYPE_NAME = 'OverflowError'
class ZeroDivisionErrorType(ArithmeticErrorType):
  TYPE_NAME = 'ZeroDivisionError'
class AssertionErrorType(StandardErrorType):
  TYPE_NAME = 'AssertionError'
class AttributeErrorType(StandardErrorType):
  TYPE_NAME = 'AttributeError'
class EnvironmentErrorType(StandardErrorType):
  TYPE_NAME = 'EnvironmentError'
class IOErrorType(EnvironmentErrorType):
  TYPE_NAME = 'IOError'
class OSErrorType(EnvironmentErrorType):
  TYPE_NAME = 'OSError'
class WindowsErrorType(OSErrorType):
  TYPE_NAME = 'OSError' # I mean WindowsError.
class VMSErrorType(OSErrorType):
  TYPE_NAME = 'OSError' # I mean VMSError.
class EOFErrorType(StandardErrorType):
  TYPE_NAME = 'EOFError'
class ImportErrorType(StandardErrorType):
  TYPE_NAME = 'ImportError'
class LookupErrorType(StandardErrorType):
  TYPE_NAME = 'LookupError'
class IndexErrorType(LookupErrorType):
  TYPE_NAME = 'IndexError'
class KeyErrorType(LookupErrorType):
  TYPE_NAME = 'KeyError'
class MemoryErrorType(StandardErrorType):
  TYPE_NAME = 'MemoryError'
class NameErrorType(StandardErrorType):
  TYPE_NAME = 'NameError'
class UnboundLocalErrorType(NameErrorType):
  TYPE_NAME = 'UnboundLocalError'
class ReferenceErrorType(StandardErrorType):
  TYPE_NAME = 'ReferenceError'
class RuntimeErrorType(StandardErrorType):
  TYPE_NAME = 'RuntimeError'
class NotImplementedErrorType(RuntimeErrorType):
  TYPE_NAME = 'NotImplementedError'
class SyntaxErrorType(StandardErrorType):
  TYPE_NAME = 'SyntaxError'
class IndentationErrorType(SyntaxErrorType):
  TYPE_NAME = 'IndentationError'
class TabErrorType(IndentationErrorType):
  TYPE_NAME = 'TabError'
class SystemErrorType(StandardErrorType):
  TYPE_NAME = 'SystemError'
class TypeErrorType(StandardErrorType):
  TYPE_NAME = 'TypeError'
class ValueErrorType(StandardErrorType):
  TYPE_NAME = 'ValueError'
class UnicodeErrorType(ValueErrorType):
  TYPE_NAME = 'UnicodeError'
class UnicodeDecodeErrorType(UnicodeErrorType):
  TYPE_NAME = 'UnicodeDecodeError'
class UnicodeEncodeErrorType(UnicodeErrorType):
  TYPE_NAME = 'UnicodeEncodeError'
class UnicodeTranslateErrorType(UnicodeErrorType):
  TYPE_NAME = 'UnicodeTranslateError'
