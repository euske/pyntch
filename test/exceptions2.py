#!/usr/bin/env python

class A: pass
class B(A): pass
class C(A): pass

try:
  raise B # this should be captured.
except A:
  print 'A'

try:
  raise A # this should not be captured
except B:
  print 'B'

try:
  raise B # this should not be captured
  raise C # this should not be captured
except (B,C):
  print 'B,C'

try:
  raise 'foo' # this should not be captured
except str:
  print 'str'
