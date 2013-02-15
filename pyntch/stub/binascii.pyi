#!/usr/bin/env python
# module: 'binascii'

class Error(Exception): pass
class Incomplete(Exception): pass

def a2b_base64(data):
  assert isinstance(data, str)
  return ''

def a2b_hex(data):
  assert isinstance(data, str)
  return ''
unhexlify = a2b_hex

def a2b_hqx(data):
  assert isinstance(data, str)
  return ''

def a2b_qp(data):
  assert isinstance(data, str)
  return ''

def a2b_uu(data):
  assert isinstance(data, str)
  return ''

def b2a_base64(data):
  assert isinstance(data, str)
  return ''

def b2a_hex(data):
  assert isinstance(data, str)
  return ''
hexlify = b2a_hex

def b2a_hqx(data):
  assert isinstance(data, str)
  return ''

def b2a_qp(data, quotetabs=0, istext=0, header=0):
  assert isinstance(data, str)
  assert isinstance(quotetabs, int)
  assert isinstance(istext, int)
  assert isinstance(header, int)
  return ''

def b2a_uu(data):
  assert isinstance(data, str)
  return ''

def crc32(data, oldcrc=0):
  assert isinstance(data, str)
  assert isinstance(oldcrc, int)
  return ''  

def crc_hqx(data, oldcrc):
  assert isinstance(data, str)
  assert isinstance(oldcrc, int)
  return ''

def rlecode_hqx(data):
  assert isinstance(data, str)
  return ''

def rledecode_hqx(data):
  assert isinstance(data, str)
  return ''
