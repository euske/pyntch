#!/usr/bin/env python

def fact(x):
  if x == 0:
    return 1
  x = x * fact(x-1)
  return x

if __name__ == '__main__':
  print fact(10)

