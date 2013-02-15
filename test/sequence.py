#!/usr/bin/env python
a = 2
t = (1,a)
l = [3,'4']

def doit(f):
  fromtuple = f(t)
  fromlist = f(l)
  err = f(a)
  null = f()
  
doit(list)
doit(tuple)

