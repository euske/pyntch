def f(x):
  assert isinstance(x, (float,int))
  return x*2

f(1)
f(2.3)
f('foo')
