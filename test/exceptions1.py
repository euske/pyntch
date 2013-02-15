#!/usr/bin/env python

class E(Exception):
  def __init__(self, *args):
    Exception.__init__(self, args)
    return

def foo():
  raise 'this should be propagated'

def bar():
  try:
    raise E('this should not be propagated')
  except E:
    pass

def baz():
  try:
    raise 'this should be propagated'
  except E, e:
    pass

def boz():
  try:
    raise 'this should be propagated'
  except:
    raise

if __name__ == '__main__':
  foo()
  bar()
  baz()
  boz()
