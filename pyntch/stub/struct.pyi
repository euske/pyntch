#!/usr/bin/env python

def calcsize(fmt):
  assert isinstance(fmt, str)
  return 0

def pack(fmt, *args):
  assert isinstance(fmt, str)
  return ''

def unpack(fmt, buf, offset=0):
  assert isinstance(fmt, str)
  assert isinstance(buf, str)
  assert isinstance(offset, int)
  return ()

