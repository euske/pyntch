#!/usr/bin/env python
import sys

BUILTIN_TYPES = ('bool', 'int', 'long', 'float', 'complex',
                 'str', 'unicode', 'list', 'tuple', 'dict')

IGNORE_TYPES = ('module','function','file','object')

def main(argv):
  args = argv[1:]
  
  def flatten(obj):
    if isinstance(obj, list):
      return [ flatten(x) for x in obj ]
    elif isinstance(obj, tuple):
      return tuple( flatten(x) for x in obj )
    elif isinstance(obj, dict):
      return dict( (flatten(k),flatten(v)) for (k,v) in obj.iteritems() )
    elif type(obj).__name__ in BUILTIN_TYPES:
      return type(obj)()
    return '???'
  
  for modname in args:
    module = __import__(modname, fromlist=1)
    print '#!/usr/bin/env python'
    print '# module: %r' % modname
    print
    for name in dir(module):
      if name.startswith('__'): continue
      obj = getattr(module, name)
      typename = type(obj).__name__
      if typename == 'type' or typename == 'classobj':
        print 'class %s:' % name
        print '  pass'
        print
      elif typename == 'builtin_function_or_method':
        print 'def %s(*x): return' % name
        print
      elif typename == 'NoneType':
        print '%s = None' % name
      elif typename in BUILTIN_TYPES:
        print '%s = %r' % (name, flatten(obj))
      elif typename in IGNORE_TYPES:
        print '%s = %s() # XXX' % (name, typename)
      else:
        print '# XXX unknown type: %s (%s)' % (name, typename)
  return 0

if __name__ == '__main__': sys.exit(main(sys.argv))
