#!/usr/bin/env python
# module: 'posix'

EX_CANTCREAT = 0
EX_CONFIG = 0
EX_DATAERR = 0
EX_IOERR = 0
EX_NOHOST = 0
EX_NOINPUT = 0
EX_NOPERM = 0
EX_NOUSER = 0
EX_OK = 0
EX_OSERR = 0
EX_OSFILE = 0
EX_PROTOCOL = 0
EX_SOFTWARE = 0
EX_TEMPFAIL = 0
EX_UNAVAILABLE = 0
EX_USAGE = 0
F_OK = 0
NGROUPS_MAX = 0
O_APPEND = 0
O_CREAT = 0
O_DIRECT = 0
O_DIRECTORY = 0
O_DSYNC = 0
O_EXCL = 0
O_LARGEFILE = 0
O_NDELAY = 0
O_NOCTTY = 0
O_NOFOLLOW = 0
O_NONBLOCK = 0
O_RDONLY = 0
O_RDWR = 0
O_RSYNC = 0
O_SYNC = 0
O_TRUNC = 0
O_WRONLY = 0
R_OK = 0
TMP_MAX = 0
WCONTINUED = 0
WNOHANG = 0
WUNTRACED = 0
W_OK = 0
X_OK = 0

class error(object): pass

class stat_result(object):
  def __init__(self):
    self.st_atime = 0
    self.st_blksize = 0
    self.st_blocks = 0
    self.st_ctime = 0
    self.st_dev = 0
    self.st_gid = 0
    self.st_ino = 0
    self.st_mode = 0
    self.st_mtime = 0
    self.st_nlink = 0
    self.st_rdev = 0
    self.st_size = 0
    self.st_uid = 0
    return
  def __len__(self):
    return 10
  def __iter__(self):
    return iter((0,0,0,0,0,0,0,0,0,0))

class statvfs_result(object):
  def __init__(self):
    self.f_bavail = 0
    self.f_bfree = 0
    self.f_blocks = 0
    self.f_bsize = 0
    self.f_favail = 0
    self.f_ffree = 0
    self.f_files = 0
    self.f_flag = 0
    self.f_frsize = 0
    self.f_namemax = 0
    return
  def __len__(self):
    return 10
  def __iter__(self):
    return iter((0,0,0,0,0,0,0,0,0,0))

_STAT = stat_result()
_STATVFS = statvfs_result()

pathconf_names = {'': 0}
sysconf_names = {'': 0}
confstr_names = {'': 0}
environ = {'': ''}

def WCOREDUMP(x):
  assert isinstance(x, int)
  return False
def WEXITSTATUS(x):
  assert isinstance(x, int)
  return 0
def WIFCONTINUED(x):
  assert isinstance(x, int)
  return False
def WIFEXITED(x):
  assert isinstance(x, int)
  return False
def WIFSIGNALED(x):
  assert isinstance(x, int)
  return False
def WIFSTOPPED(x):
  assert isinstance(x, int)
  return False
def WSTOPSIG(x): 
  assert isinstance(x, int)
  return 0
def WTERMSIG(x):
  assert isinstance(x, int)
  return 0

def _exit(x):
  assert isinstance(x, int)
  return

def abort(): return

def access(path, mode):
  assert isinstance(path, str)
  assert isinstance(mode, int)
  return

def chdir(path):
  assert isinstance(path, str)
  return

def chmod(path, mode):
  assert isinstance(path, str)
  assert isinstance(mode, int)
  return

def chown(path, uid, gid):
  assert isinstance(path, str)
  assert isinstance(uid, int)
  assert isinstance(gid, int)
  return

def chroot(path):
  assert isinstance(path, str)
  return

def close(fd):
  assert isinstance(fd, int)
  return

def confstr(x): return ''

def ctermid(): return ''

def dup(fd):
  assert isinstance(fd, int)
  return 0

def dup2(fd1,fd2):
  assert isinstance(fd1, int)
  assert isinstance(fd2, int)
  return

def execv(path, args):
  assert isinstance(path, str)
  for arg in args:
    assert isinstance(arg, str)
  return

def execve(path, args, env):
  assert isinstance(path, str)
  for arg in args:
    assert isinstance(arg, str)
  for (k,v) in env.iteritems():
    assert isinstance(k, str)
    assert isinstance(v, str)
  return

def fchdir(fd):
  assert isinstance(fd, int)
  return

def fdatasync(fd):
  assert isinstance(fd, int)
  return

def fdopen(fd, mode='', bufsize=0):
  assert isinstance(fd, int)
  assert isinstance(mode, str)
  assert isinstance(bufsize, int)
  return file('')

def fork():
  return 0

def forkpty(pid, fd):
  assert isinstance(pid, int)
  assert isinstance(fd, int)
  return 0

def fpathconf(fd, name):
  assert isinstance(fd, int)
  assert isinstance(name, str)
  return 0

def fstat(fd):
  assert isinstance(fd, int)
  return _STAT

def fstatvfs(fd):
  assert isinstance(fd, int)
  return _STATVFS

def fsync(fd):
  assert isinstance(fd, int)
  return

def ftruncate(fd, length):
  assert isinstance(fd, int)
  assert isinstance(length, int)
  return

def getcwd():
  return ''

def getcwdu():
  return u''

def getegid():
  return 0

def geteuid():
  return 0

def getgid():
  return 0

def getgroups():
  return [0]

def getloadavg():
  return (0.0, 0.0, 0.0)

def getlogin():
  return ''

def getpgid(pid):
  assert isinstance(pid, int)
  return 0

def getpgrp():
  return 0

def getpid():
  return 0

def getppid():
  return 0

def getsid():
  return 0

def getuid():
  return 0

def isatty():
  return False

def kill(pid, sig):
  assert isinstance(pid, int)
  assert isinstance(sig, int)
  return

def killpg(pid, sig):
  assert isinstance(pid, int)
  assert isinstance(sig, int)
  return

def lchown(path, uid, gid):
  assert isinstance(path, str)
  assert isinstance(uid, int)
  assert isinstance(gid, int)
  return

def link(src, dst):
  assert isinstance(src, str)
  assert isinstance(dst, str)
  return

def listdir(path):
  assert isinstance(path, str)
  return ['']

def lseek(fd, pos, how):
  assert isinstance(fd, int)
  assert isinstance(pos, int)
  assert isinstance(how, int)
  return

def lstat(path):
  assert isinstance(path, str)
  return _STAT

def major(dev):
  assert isinstance(dev, int)
  return 0

def makedev(major, minor):
  assert isinstance(major, int)
  assert isinstance(minor, int)
  return 0

def minor(dev):
  assert isinstance(dev, int)
  return 0

def mkdir(path, mode=0):
  assert isinstance(path, str)
  assert isinstance(mode, int)
  return

def mkfifo(path, mode=0):
  assert isinstance(path, str)
  assert isinstance(mode, int)
  return

def mknod(path, mode=0, dev=0):
  assert isinstance(path, str)
  assert isinstance(mode, int)
  assert isinstance(dev, int)
  return

def nice(prio):
  assert isinstance(prio, int)
  return 0

def open(path, flag, mode=0):
  assert isinstance(path, str)
  assert isinstance(flag, int)
  assert isinstance(mode, int)
  return 0

def openpty():
  return (0, 0)

def pathconf(path, name):
  assert isinstance(path, str)
  assert isinstance(name, str)
  return 0

def pipe():
  return (0, 0)

def popen(cmd, mode='', bufsize=0):
  assert isinstance(cmd, str)
  assert isinstance(mode, str)
  assert isinstance(bufsize, int)
  return 0

def putenv(k, v):
  assert isinstance(k, str)
  assert isinstance(v, str)
  return

def read(fd, bufsize):
  assert isinstance(fd, int)
  assert isinstance(bufsize, int)
  return ''

def readlink(path):
  assert isinstance(path, str)
  return ''

def remove(path):
  assert isinstance(path, str)
  return

def rename(old, new):
  assert isinstance(old, str)
  assert isinstance(new, str)
  return

def rmdir(path):
  assert isinstance(path, str)
  return

def setegid(gid):
  assert isinstance(gid, int)
  return

def seteuid(uid):
  assert isinstance(uid, int)
  return

def setgid(gid):
  assert isinstance(gid, int)
  return

def setgroups(groups):
  for gid in groups:
    assert isinstance(gid, int)
  return

def setpgid(pid, pgrp):
  assert isinstance(pid, int)
  assert isinstance(pgrp, int)
  return

def setpgrp(): return

def setregid(rgid, egid):
  assert isinstance(rgid, int)
  assert isinstance(egid, int)
  return

def setreuid(ruid, euid):
  assert isinstance(ruid, int)
  assert isinstance(euid, int)
  return

def setsid(): return

def setuid(uid):
  assert isinstance(uid, int)
  return

def stat(path):
  assert isinstance(path, str)
  return _STAT

def stat_float_times(newval=False):
  return True

def statvfs(path):
  return _STATVFS

def strerror(code):
  assert isinstance(code, int)
  return ''

def symlink(src, dst):
  assert isinstance(src, str)
  assert isinstance(dst, str)
  return

def sysconf(name):
  assert isinstance(name, str)
  return 0

def system(cmd):
  assert isinstance(cmd, str)
  return 0

def tcgetpgrp(fd):
  assert isinstance(fd, int)
  return 0

def tcsetpgrp(fd, pgid):
  assert isinstance(fd, int)
  assert isinstance(pgid, int)
  return

def tempnam(dir='', prefix=''):
  assert isinstance(dir, str)
  assert isinstance(prefix, str)
  return ''

def times():
  return (0.0, 0.0, 0.0, 0.0, 0.0)

def tmpfile():
  return file('')

def tmpnam():
  return ''

def ttyname(fd):
  assert isinstance(fd, int)
  return

def umask(mask):
  assert isinstance(mask, int)
  return

def uname():
  return ('', '', '', '', '')

unlink = remove

def unsetenv(k):
  assert isinstance(k, str)
  return

def utime(path, x):
  assert isinstance(path, str)
  return

def wait():
  return (0, 0)

def wait3(opts):
  assert isinstance(opts, int)
  return (0, 0, 0)

def wait4(pid, opts):
  assert isinstance(pid, int)
  assert isinstance(opts, int)
  return (0, 0, 0)

def waitpid(pid, opts):
  assert isinstance(pid, int)
  assert isinstance(opts, int)
  return (0, 0)

def write(fd, data):
  assert isinstance(fd, int)
  assert isinstance(data, str)
  return

