#!/usr/bin/env python

class error(Exception): pass

def hash(x):
  assert isinstance(x, str)
  return 0

class init(object):
  
  def __init__(self, fname):
    assert isinstance(fname, str)
    self.fd = 0
    self.name = fname
    self.size = 0
    return

  def __getitem__(self, k):
    assert isinstance(k, str)
    if 0:
      raise KeyError(k)
    else:
      return ''

  def get(self, k):
    assert isinstance(k, str)
    return ''

  def getall(self, k):
    assert isinstance(k, str)
    return ['']

  def has_key(self, k):
    assert isinstance(k, str)
    return 0

  def each(self):
    if 0:
      return None
    else:
      return ('', '')

  def keys(self):
    return ['']

  def firstkey(self):
    if 0:
      return None
    else:
      return ''

  def nextkey(self):
    if 0:
      return None
    else:
      return ''

class cdbmake(object):
  
  def __init__(self, fname, tmpname):
    assert isinstance(fname, str)
    assert isinstance(tmpname, str)
    return

  def add(self, k, v):
    assert isinstance(k, str)
    assert isinstance(v, str)
    return

  def finish(self):
    return
