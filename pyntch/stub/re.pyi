#!/usr/bin/env python

I = IGNORECASE = 0
L = LOCALE = 0
U = UNICODE = 0
M = MULTILINE = 0
S = DOTALL = 0
X = VERBOSE = 0
T = TEMPLATE = 0
DEBUG = 0

class Match(object):
  def group(self, i=0):
    assert isinstance(i, int)
    return ''
  def groups(self):
    return ['']
  def start(self, i=0):
    assert isinstance(i, int)
    return 0
  def end(self, i=0):
    assert isinstance(i, int)
    return 0

class Pattern(object):
  def __init__(self, pattern='', flags=0):
    assert isinstance(pattern, str)
    assert isinstance(flags, int)
    return
  def search(self, string, flags=0):
    assert isinstance(string, basestring)
    assert isinstance(flags, int)
    if 1:
      return None
    else:
      return Match()
  def match(self, string, flags=0):
    assert isinstance(string, basestring)
    assert isinstance(flags, int)
    if 1:
      return None
    else:
      return Match()
  def sub(self, repl, string, count=0):
    assert isinstance(string, basestring)
    assert isinstance(count, int)
    return ''
  def subn(self, repl, string, count=0):
    assert isinstance(string, basestring)
    assert isinstance(count, int)
    return ('', 0)
  def split(self, string, maxsplit=0):
    assert isinstance(string, basestring)
    assert isinstance(maxsplit, int)
    return ['']
  def findall(self, string, flags=0):
    assert isinstance(string, basestring)
    assert isinstance(flags, int)
    return ['']
  def finditer(self, string, flags=0):
    assert isinstance(string, basestring)
    assert isinstance(flags, int)
    return [Match()]

compile = Pattern
def match(pattern, string, flags=0):
  return Pattern(pattern, flags).match(string)
def search(pattern, string, flags=0):
  return Pattern(pattern, flags).search(string)
def sub(pattern, repl, string, count=0):
  return Pattern(pattern).sub(repl, string, count)
def subn(pattern, repl, string, count=0):
  return Pattern(pattern).subn(repl, string, count)
def split(pattern, string, maxsplit=0):
  return Pattern(pattern).split(string, maxsplit)
def findall(pattern, string, flags=0):
  return Pattern(pattern, flags).findall(string)
def finditer(pattern, string, flags=0):
  return Pattern(pattern, flags).finditer(string)
def escape(pattern):
  assert isinstance(pattern, basestring)
  return ''
