#!/usr/bin/env python

import sys, os, os.path, time
import pyntch
from pyntch.typenode import TypeNode, CompoundTypeNode, TypeChecker
from pyntch.frame import ExecutionFrame, ExceptionCatcher
from pyntch.expression import MustBeDefinedNode
from pyntch.namespace import Namespace
from pyntch.module import Interpreter, IndentedStream, ModuleNotFound
from pyntch.config import ErrorConfig

# main
def main(argv):
  import getopt
  def usage():
    print 'usage: %s [-d] [-q] [-a] [-c config] [-C key=val] [-D] [-p pythonpath] [-P stubpath] [-o output] [-t format] [file ...]' % argv[0]
    return 100
  try:
    (opts, args) = getopt.getopt(argv[1:], 'dqac:CDp:P:o:t:')
  except getopt.GetoptError:
    return usage()
  if not args:
    return usage()
  stubdir = os.path.join(os.path.dirname(pyntch.__file__), 'stub')
  debug = 0
  defaultpath = True
  showall = False
  format = 'txt'
  verbose = 1
  modpath = []
  stubpath = [stubdir]
  output = None
  for (k, v) in opts:
    if k == '-d': debug += 1
    elif k == '-q': verbose -= 1
    elif k == '-a': showall = True
    elif k == '-c': ErrorConfig.load(v)
    elif k == '-C':
      (k,v) = v.split('=')
      ErrorConfig.set(k, eval(v))
    elif k == '-D': defaultpath = False
    elif k == '-p': modpath.extend(v.split(':'))
    elif k == '-P': stubpath.extend(v.split(':'))
    elif k == '-o':
      output = v
      if v.endswith('.xml'):
        format = 'xml'
    elif k == '-t': format = v
  if defaultpath:
    modpath.extend(sys.path)
  TypeNode.debug = debug
  TypeNode.verbose = verbose
  Interpreter.debug = debug
  Interpreter.verbose = verbose
  Interpreter.initialize(stubpath)
  TypeChecker.reset()
  MustBeDefinedNode.reset()
  ExceptionCatcher.reset()
  t = time.time()
  modules = []
  for name in args:
    try:
      if name.endswith('.py'):
        path = name
        (name,_) = os.path.splitext(os.path.basename(name))
        modules.append(Interpreter.load_file(name, path, modpath))
      else:
        modules.append(Interpreter.load_module(name, modpath)[-1])
    except ModuleNotFound, e:
      print >>sys.stderr, 'module not found:', name
  if showall:
    modules = Interpreter.get_all_modules()
  if ErrorConfig.unfound_modules:
    print >>sys.stderr, 'modules not found:', ', '.join(sorted(ErrorConfig.unfound_modules))
  TypeNode.run()
  TypeChecker.check()
  MustBeDefinedNode.check()
  ExceptionCatcher.check()
  TypeNode.run()
  if verbose:
    print >>sys.stderr, ('total files=%d, lines=%d in %.2fsec' %
                         (Interpreter.files, Interpreter.lines, time.time()-t))
  outfp = sys.stdout
  if output:
    outfp = file(output, 'w')
  strm = IndentedStream(outfp)
  if format == 'xml': strm.write('<output>')
  for module in modules:
    if format == 'xml':
      module.showxml(strm)
    else:
      module.showtxt(strm)
  if format == 'xml': strm.write('</output>')
  return 0

if __name__ == '__main__': sys.exit(main(sys.argv))
