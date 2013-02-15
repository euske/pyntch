#!/usr/bin/env python

def fact(x):
  if x == 0:
    return 'A'
  return x * fact(fact(x)+'B')

if __name__ == '__main__':
  print fact(10)

