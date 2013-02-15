a='global'

class B:
  print 1, a
  a='B'
  print 2, a
  
class A(B):
  print 3, a
  #a='A'
  print 4, a

  def __init__(self):
    self.a = 'instance'
    print 7, a, self.a
    
  #@classmethod
  def foo(klass):
    print 8, a, klass.a
  
  @staticmethod
  def bar():
    print 9, a, A.a

print 5, B.a
print 6, A.a
x=A()
A.foo()
A.bar()
