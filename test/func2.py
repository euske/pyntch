#!/usr/bin/env python

f = (lambda x: (lambda y: x(y)))

while 1:
  print f
  f=f(f)
