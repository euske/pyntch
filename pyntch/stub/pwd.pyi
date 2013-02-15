#!/usr/bin/env python
# module: 'pwd'

class struct_passwd:
  pass

class struct_pwent:
  pass

_ENTRY = ('', '', 0, 0, '', '', '')

def getpwall():
  return []

def getpwnam(name):
  assert isinstance(name, str)
  return _ENTRY

def getpwuid(uid):
  assert isinstance(uid, int)
  return _ENTRY
