#!/usr/bin/env python
# module: 'sys'

api_version = 0
argv = ['']
builtin_module_names = ['']
byteorder = ''
copyright = ''
exc_type = None
exec_prefix = ''
executable = ''
hexversion = 0
maxint = 0
maxunicode = 0
meta_path = []
path = ['']
platform = ''
prefix = ''
pydebug = False
try:
  stderr = file('')
  stdin = file('')
  stdout = file('')
except:
  pass
subversion = ('', '', '')
version = ''
version_info = (0, 0, 0, '', 0)
warnoptions = ['']
modules = {'':None}

class frame(object): pass

def _current_frames(): return { 0: frame() }
def _getframe(): return frame()
def call_tracing(func,args): return func(*args)
def callstats(): return None
def displayhook(x): return 0
def exc_clear(): return
def exc_info(): return (None, None, None)
def excepthook(x,y,z): return
def exit(x=None): return
def getcheckinterval(): return 0
def getdefaultencoding(): return ''
def getdlopenflags(): return 0
def getfilesystemencoding(): return ''
def getrecursionlimit(): return 0
def getrefcount(x): return 0
def setcheckinterval(x): assert isinstance(x, int)
def setdefaultencoding(x): assert isinstance(x, str)
def setdlopenflags(x): assert isinstance(x, int)
def setprofile(x): return
def setrecursionlimit(x): assert isinstance(x, int)
def settrace(x): assert isinstance(x, int)
