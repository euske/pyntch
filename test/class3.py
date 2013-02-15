#!/usr/bin/env python

class A(object):
  
  def __init__(self, x):
    self.x = x
    return
  
  def __repr__(self):
    return '<%r>' % self.x
  
  def __str__(self):
    return 123
  
  def __eq__(self, a):
    return self.x == a.x

  def __add__(self, obj):
    return 123

  def __iter__(self):
    return iter([1])
  

a = A('a')
b = A('a')
print a
c = (a == b)
d = (a + b)
e = list(a)
print e
