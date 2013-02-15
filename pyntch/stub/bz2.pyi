#!/usr/bin/env python
# module: 'bz2'

class BZ2Compressor:
  def __init__(self, level):
    assert isinstance(level, int)
    return
  def compress(self, data):
    assert isinstance(data, str)
    return ''
  def flush(self):
    return ''

class BZ2Decompressor:
  def decompress(self, data):
    assert isinstance(data, str)
    return ''

class BZ2File:
  def __init__(self, name, mode='', buffering=0, compresslevel=9):
    assert isinstance(name, str)
    assert isinstance(mode, str)
    assert isinstance(buffering, int)
    assert isinstance(compresslevel, int)
    return

def compress(data, compresslevel=0):
  assert isinstance(data, str)
  assert isinstance(level, int)
  return ''

def decompress(data):
  assert isinstance(data, str)
  return ''
