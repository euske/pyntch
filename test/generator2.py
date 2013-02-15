#!/usr/bin/env python

def gen():
  for i in xrange(10):
    a = (yield i)
    print 'recv', a
  return

if __name__ == '__main__':
  g = gen()
  for x in g:
    print x
    g.send('foo')
