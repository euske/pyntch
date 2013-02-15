#!/usr/bin/env python
import sys, os.path
try:
  from xml.etree.cElementTree import ElementTree
except ImportError:
  from xml.etree.ElementTree import ElementTree

def dumpobj(e):
  if e.tag == 'compound':
    if e.getchildren():
      return '|'.join( dumpobj(c) for c in e.getchildren() )
    else:
      return '?'
  elif e.tag == 'list':
    return '[%s]' % dumpobj(e[0])
  elif e.tag == 'set':
    return '([%s])' % dumpobj(e[0])
  elif e.tag == 'dict':
    return '{%s: %s}' % (dumpobj(e[0]), dumpobj(e[1]))
  elif e.tag == 'iter':
    return '(%s, ...)' % dumpobj(e[0])
  elif e.tag == 'tuple':
    if e.get('len'):
      return '(%s)' % ','.join( dumpobj(c) for c in e.getchildren() )
    else:
      return '(*%s)' % dumpobj(e[0])
  elif e.tag == 'ref':
    return '...'
  elif e.tag in ('class', 'instance', 'method', 'boundmethod', 'function', 'module'):
    return '<%s %s>' % (e.tag, e.get('name'))
  else:
    return '<%s>' % e.tag

def getlineno(loc):
  r = loc.split(':')
  if len(r) == 2:
    return (int(r[1]), int(r[1]))
  else:
    return (int(r[1]), int(r[2]))

def annot(fp, module):
  lines = {}
  def add(n, x):
    n -= 1
    if n not in lines: lines[n] = []
    lines[n].append(x)
    return
  def rec(e):
    for c in e.getchildren():
      if c.tag in ('module', 'class', 'function'):
        rec(c)
      elif c.tag in ('var', 'arg'):
        add(n, '# %s = %s' % (c.get('name'), dumpobj(c[0])))
      elif c.tag == 'classattr':
        add(n, '# class.%s = %s' % (c.get('name'), dumpobj(c[0])))
      elif c.tag == 'instanceattr':
        add(n, '# instance.%s = %s' % (c.get('name'), dumpobj(c[0])))
      elif c.tag == 'return':
        add(n, '# return %s' % dumpobj(c[0]))
      elif c.tag == 'raise':
        (i,_) = getlineno(c.get('loc'))
        add(i, '# raise %s' % c.get('msg'))
      elif c.tag == 'caller':
        add(n, '# caller: %s' % c.get('loc'))
    return
  rec(module)
  for (i,line) in enumerate(fp):
    line = line.rstrip()
    if i in lines:
      n = len(line)-len(line.lstrip())
      for x in lines[i]:
        print ' '*n+x
    print line
  return

# main
def main(argv):
  import getopt
  def usage():
    print 'usage: %s [-d] [-p basedir] xml files ...' % argv[0]
    return 100
  try:
    (opts, args) = getopt.getopt(argv[1:], 'dp:')
  except getopt.GetoptError:
    return usage()
  if not args:
    return usage()
  debug = 0
  basedir = '.'
  for (k, v) in opts:
    if k == '-d': debug += 1
    elif k == '-p': basedir = v
  modules = {}
  root = ElementTree().parse(args.pop(0))
  for module in root.getchildren():
    if module.tag != 'module': continue
    modules[module.get('name')] = module
    modules[module.get('src')] = module
  for name in args:
    try:
      module = modules[name]
    except KeyError:
      print >>sys.stderr, 'not found: %r' % name
      continue
    src = os.path.join(basedir, module.get('src'))
    fp = file(src)
    annot(fp, module)
    fp.close()
  return 0

if __name__ == '__main__': sys.exit(main(sys.argv))
