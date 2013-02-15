#!/usr/bin/env python

def foo(x):
  print 'foo', x
  if x == 0:
    return 0
  return bar(x-1)

def bar(y):
  print 'bar', y
  if y == 0:
    return 1
  return foo(y+'a')

if __name__ == '__main__':
  print foo(10)
  print bar(10)
