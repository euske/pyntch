#!/usr/bin/env python

a1 = {1:2, 3:4}
a2 = dict(a=2, b=3)
a2['b'] = 'c'
a3 = dict(1)
a4 = dict([1,2,3])
a5 = dict([(1,2),(3,4,5)])
a6 = dict([('a','b'),('c','d')])

b1 = a1.get(3)
b2 = a1.get(3,4)
b3 = a2.pop(1)
b4 = a2.pop(1,2)
b5 = a2.popitem()
b6 = a6.setdefault(1,2)

a1.clear()

c1 = a1.copy()
c1['x'] = 'y'

d1 = {}.fromkeys(1)
d2 = {}.fromkeys([1,2,3])
d3 = {}.fromkeys([1,2,3], 'b')
d4 = dict.fromkeys([1,2,3])
d2.update({'a':2})
d2.update([(1,'b')])

e1 = a1.has_key('abc')
e2 = a2.items()
e3 = a2.keys()
e4 = a2.values()
e5 = a2.iteritems()
e6 = a2.iterkeys()
e7 = a2.itervalues()

