#!/usr/bin/env python

a1 = set()
a2 = set([1,2,3])
a3 = set((1,2,3))
a4 = a2.copy()

a1.add('a')
a4.add('a')
a1.clear()
a1.remove(1)
a1.discard(1)
a3.update(a1)

b2 = a2[0]
b3 = a1.pop()
b4 = a1.issubset(a2)
b5 = a2.issuperset(a2)

c1 = a1.difference(a2)
c2 = a2.intersection(a3)
c3 = a1.union(a2)
