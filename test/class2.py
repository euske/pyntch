#!/usr/bin/env python

class A(object):
  def __init__(self, x):
    self.x = x
    return
  def foo(self):
    return 0

class B(A):
  def __init__(self):
    A.__init__(self, '123')
    return
  def foo(self):
    return ''
  def bar(self):
    return 123

class C(B):
  def bar(self):
    return 0.12

a = A(123)
b = B()
c = C()

d = a.foo()
e = b.foo()
f = b.bar()
g = c.foo()
h = c.bar()
