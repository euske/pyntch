#!/usr/bin/env python

def asctime(x):
  return ''

def clock():
  return 0.0

def time():
  return 0.0

def ctime(x=0):
  assert isinstance(x, int)
  return ''

def gmtime(x=0):
  assert isinstance(x, int)
  return (0,0,0,0,0,0,0,0,0)

def localtime(x=0):
  assert isinstance(x, int)
  return (0,0,0,0,0,0,0,0,0)

def mktime((_,_,_,_,_,_,_,_,_)):
  return 0.0

def sleep(x):
  assert isinstance(x, int)
  return

def strftime(fmt, tup=(0,0,0,0,0,0,0,0,0)):
  assert isinstance(fmt, str)
  (_,_,_,_,_,_,_,_,_) = tup
  return ''
