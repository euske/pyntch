#!/usr/bin/python

def foo(a,b):
  print (a,b)

def bar(a,(b,c),*d,**e):
  print (a,b,c,d,e)

def baz(a,b=2,(c,d)=(3,'b'),**e):
  print (a,b,c,d,e)

foo(1,2)
foo(a=1,b=2)
foo(1,a=1)
foo(1,b=1)
foo(*(1,))
foo(*(1,2))
foo(*(1,2,3))

bar(1,2)
bar(1,(2,3),4,5)
bar(1,b=2,c=3)
bar(1,2,c=2)
bar(1,2,3,d=1,z='z')
