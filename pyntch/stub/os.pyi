#!/usr/bin/env python
# module: 'os'

from posix import *
import errno
import posixpath as path

SEEK_CUR = 0
SEEK_END = 0
SEEK_SET = 0

name = 'posix'
curdir = ''
pardir = ''
sep = ''
extsep = ''
altsep = ''
pathsep = ''
linesep = ''
defpath = ''
devnull = ''

class error(EnvironmentError):
  pass

OSError = error
WindowsError = error
VMSError = error

def execl(file, *args):
  execv(file, args)
  return
def execle(file, *args):
  execve(file, args[:-1], args[-1])
  return
execlp = execl
execlpe = execle
execvp = execv
execvpe = execve

def getenv(k):
  assert isinstance(k, str)
  return environ[k]

def popen2(cmd, mode='', bufsize=0):
  assert isinstance(cmd, str)
  assert isinstance(mode, str)
  assert isinstance(bufsize, int)
  return (file(''), file(''))
def popen3(cmd, mode='', bufsize=0):
  assert isinstance(cmd, str)
  assert isinstance(mode, str)
  assert isinstance(bufsize, int)
  return (file(''), file(''), file(''))
def popen4(cmd, mode='', bufsize=0):
  assert isinstance(cmd, str)
  assert isinstance(mode, str)
  assert isinstance(bufsize, int)
  return (file(''), file(''))

def makedirs(path, mode=0):
  assert isinstance(path, str)
  assert isinstance(mode, int)
  return
def removedirs(path):
  assert isinstance(path, str)
  return
def renames(old, new):
  assert isinstance(old, str)
  assert isinstance(new, str)
  return

P_NOWAIT = 0
P_NOWAITO = 0
P_WAIT = 0

def spawnv(mode, file, args):
  return
def spawnve(mode, file, args, env):
  return
def spawnl(mode, file, *args):
  return spawnv(mode, file, args)
def spawnle(mode, file, *args):
  return spawnve(mode, file, args[:-1], args[-1])
spawnvp = spawnv
spawnvpe = spawnve
spawnlp = spawnl
spawnlpe = spawnle

def urandom(n):
  assert isinstance(n, int)
  return ''

def walk(top, topdown=True, onerror=None):
  return
