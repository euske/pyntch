#!/usr/bin/env python

def makeloop(x):
  x[0] = x
  return

a = [1,2,3]
makeloop(a)
b = [4,5,6]
makeloop(b)

c = a
c = b
print a+b+c
