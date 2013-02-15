#!/usr/bin/env python
# module: 'imp'

C_BUILTIN = 0
C_EXTENSION = 0
IMP_HOOK = 0
PKG_DIRECTORY = 0
PY_CODERESOURCE = 0
PY_COMPILED = 0
PY_FROZEN = 0
PY_RESOURCE = 0
PY_SOURCE = 0
SEARCH_ERROR = 0

class NullImporter(object):
  def find_module(*x):
    return None

def acquire_lock(*x): return

def find_module(*x): return

def get_frozen_object(*x): return

def get_magic(*x): return

def get_suffixes(*x): return

def init_builtin(*x): return

def init_frozen(*x): return

def is_builtin(*x): return

def is_frozen(*x): return

def load_compiled(*x): return

def load_dynamic(*x): return

def load_module(*x): return

def load_package(*x): return

def load_source(*x): return

def lock_held(*x): return

def new_module(*x): return

def release_lock(*x): return

