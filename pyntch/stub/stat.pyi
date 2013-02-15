#!/usr/bin/env python
# module: 'stat'

ST_ATIME = 0
ST_CTIME = 0
ST_DEV = 0
ST_GID = 0
ST_INO = 0
ST_MODE = 0
ST_MTIME = 0
ST_NLINK = 0
ST_SIZE = 0
ST_UID = 0
S_ENFMT = 0
S_IEXEC = 0
S_IFBLK = 0
S_IFCHR = 0
S_IFDIR = 0
S_IFIFO = 0
S_IFLNK = 0
S_IFREG = 0
S_IFSOCK = 0
S_IREAD = 0
S_IRGRP = 0
S_IROTH = 0
S_IRUSR = 0
S_IRWXG = 0
S_IRWXO = 0
S_IRWXU = 0
S_ISGID = 0
S_ISUID = 0
S_ISVTX = 0
S_IWGRP = 0
S_IWOTH = 0
S_IWRITE = 0
S_IWUSR = 0
S_IXGRP = 0
S_IXOTH = 0
S_IXUSR = 0

def S_IFMT(mode):
  assert isinstance(mode, int)
  return 0
def S_IMODE(mode):
  assert isinstance(mode, int)
  return 0

def S_ISBLK(mode):
  assert isinstance(mode, int)
  return False
def S_ISCHR(mode):
  assert isinstance(mode, int)
  return False
def S_ISDIR(mode):
  assert isinstance(mode, int)
  return False
def S_ISFIFO(mode):
  assert isinstance(mode, int)
  return False
def S_ISLNK(mode):
  assert isinstance(mode, int)
  return False
def S_ISREG(mode):
  assert isinstance(mode, int)
  return False
def S_ISSOCK(mode):
  assert isinstance(mode, int)
  return False
