#!/usr/bin/env python
# module: 'zlib'

DEFLATED = 0
DEF_MEM_LEVEL = 0
MAX_WBITS = 0
ZLIB_VERSION = ''
Z_BEST_COMPRESSION = 0
Z_BEST_SPEED = 0
Z_DEFAULT_COMPRESSION = 0
Z_DEFAULT_STRATEGY = 0
Z_FILTERED = 0
Z_FINISH = 0
Z_FULL_FLUSH = 0
Z_HUFFMAN_ONLY = 0
Z_NO_FLUSH = 0
Z_SYNC_FLUSH = 0

def adler32(data, start=0):
  assert isinstance(data, str)
  assert isinstance(start, int)
  return 0

def crc32(data, start=0):
  assert isinstance(data, str)
  assert isinstance(start, int)
  return 0

def compress(data, level=0):
  assert isinstance(data, str)
  assert isinstance(level, int)
  return ''

def decompress(data, wbits=0, bufsize=0):
  assert isinstance(data, str)
  assert isinstance(wbits, int)
  assert isinstance(bufsize, int)
  return ''

class error(Exception): pass

class compressobj(object):
  def __init__(self, level):
    assert isinstance(level, int)
    return
  def compress(self, data):
    assert isinstance(data, str)
    return ''
  def flush(self):
    return ''

class decompressobj(object):
  def __init__(self, wbits):
    assert isinstance(wbits, int)
    return
  def decompress(self, data):
    assert isinstance(data, str)
    return ''
  def flush(self):
    return ''
