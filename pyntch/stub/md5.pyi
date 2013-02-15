#!/usr/bin/env python

blocksize = 0
digest_size = 0

class md5(object):
  blocksize = 0
  digest_size = 0
  def __init__(self, data=''):
    assert isinstance(data, str)
    return
  def copy(self):
    return self
  def digest(self):
    return ''
  def hexdigest(self):
    return ''
  def update(self, data):
    assert isinstance(data, str)
    return

new = md5
