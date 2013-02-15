#!/usr/bin/env python

def foo(x):
  class A:
    a = x
    def __init__(self):
      self.x = str(x)
      return
  b = A()
  print (A.a, b.x)
  return b

foo(123)
