#!/usr/bin/env python

def disp(n):
  for i in (1,2,3):
    yield (i,i*2,i*3)
  return

if __name__ == '__main__':
  for (a,b,c) in disp(10):
    print a
