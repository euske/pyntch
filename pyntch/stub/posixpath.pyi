#!/usr/bin/env python
# module: 'posixpath'

altsep = None
curdir = ''
defpath = ''
devnull = ''
extsep = ''
pardir = ''
pathsep = ''
sep = ''
supports_unicode_filenames = False

def abspath(path):
  assert isinstance(path, basestring)
  return path

def basename(path):
  assert isinstance(path, basestring)
  return path

def commonprefix(m):
  for path in m:
    assert isinstance(path, basestring)
  return path

def dirname(path):
  assert isinstance(path, basestring)
  return path

def exists(path):
  assert isinstance(path, basestring)
  return False

def expanduser(path):
  assert isinstance(path, basestring)
  return path
def expandvars(path):
  assert isinstance(path, basestring)
  return path

def getatime(path):
  assert isinstance(path, basestring)
  return 0
def getctime(path):
  assert isinstance(path, basestring)
  return 0
def getmtime(path):
  assert isinstance(path, basestring)
  return 0
def getsize(path):
  assert isinstance(path, basestring)
  return 0

def isabs(path):
  assert isinstance(path, basestring)
  return False
def isdir(path):
  assert isinstance(path, basestring)
  return False
def isfile(path):
  assert isinstance(path, basestring)
  return False
def islink(path):
  assert isinstance(path, basestring)
  return False
def ismount(path):
  assert isinstance(path, basestring)
  return False

def join(path, *m):
  assert isinstance(path, basestring)
  for p in m:
    assert isinstance(p, basestring)
  return path

def lexists(path):
  assert isinstance(path, basestring)
  return False

def normcase(path):
  assert isinstance(path, basestring)
  return path
def normpath(path):
  assert isinstance(path, basestring)
  return path
def realpath(path):
  assert isinstance(path, basestring)
  return path

def samefile(path):
  assert isinstance(path, basestring)
  return False
def sameopenfile(path):
  assert isinstance(path, basestring)
  return False
def samestat(path):
  assert isinstance(path, basestring)
  return False

def split(path):
  assert isinstance(path, basestring)
  return (path, path)
  
def splitext(path):
  assert isinstance(path, basestring)
  return (path, path)

def splitdrive(path):
  assert isinstance(path, basestring)
  return (path, path)

def walk(top, func, arg):
  assert isinstance(top, basestring)
  func(arg, top, [''])
  return
