#!/usr/bin/env python

def foo(x,y):
  return x+y

def bar():
  try:
    foo(1,'a')
  except ValueError:
    pass

bar()
