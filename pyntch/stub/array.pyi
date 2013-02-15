#!/usr/bin/env python

class ArrayType(object):
  
  def __init__(self, typecode, initializer=[]):
    assert isinstance(typecode, str)
    self.seq = []
    for x in initializer:
      self.seq.append(x)
    return

  def __len__(self):
    return 0

  def append(self, x):
    self.seq.append(x)
    return

  def buffer_info(self):
    return (0, 0)

  def byteswap(self):
    return

  def count(self, x):
    return 0

  def extend(self, seq):
    return

  def fromfile(self, fp, n):
    assert isinstance(fp, file)
    assert isinstance(n, int)
    return

  def fromstring(self, data):
    assert isinstance(data, str)
    return

  def fromunicode(self, data):
    assert isinstance(data, unicode)
    return

  def index(self, x):
    return 0

  def insert(self, i, x):
    assert isinstance(i, int)
    self.seq.append(x)
    return

  def pop(self):
    return self.seq.pop()

  def remove(self, x):
    self.seq.remove(x)
    return

  def tofile(self, fp):
    return
  
  def tolist(self):
    return self.seq
  
  def tostring(self):
    return ''
  
  def tounicode(self):
    return u''
  
  read = fromfile
  write = tofile

array = ArrayType
