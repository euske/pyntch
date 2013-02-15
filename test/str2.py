#!/usr/bin/env python

class A:
  def __repr__(self):
    return '<A>'
  def __str__(self):
    return 123

a = A()
b = str(a)
