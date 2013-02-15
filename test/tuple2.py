#!/usr/bin/env python

def tree(n):
  if n == 1:
    return (0,'o')
  if n == 2:
    return 2
  return (n, tree(n-1), tree(n-2))
  

if __name__ == '__main__':
  a = tree(5)
  print a
