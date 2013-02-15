#!/usr/bin/env python
import sys, compiler

def main(argv):
  for fname in argv[1:]:
    tree = compiler.parseFile(fname)
    print tree
  return 0

if __name__ == '__main__': sys.exit(main(sys.argv))
