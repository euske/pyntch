#!/usr/bin/env python

class A(object):
  a = 1
  #b = 2
  
  def __init__(self, x):
    self.x = x
    self.a = 'a'
    A.b = 2
    return
  
  def foo(self, y):
    self.x = y
    return self.b

p = A(123)
q = p.foo('456')
r = p.zzz # AttributeError
