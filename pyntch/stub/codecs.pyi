#!/usr/bin/env python
# module: 'codecs'

BOM = ''
BOM32_BE = ''
BOM32_LE = ''
BOM64_BE = ''
BOM64_LE = ''
BOM_BE = ''
BOM_LE = ''
BOM_UTF16 = ''
BOM_UTF16_BE = ''
BOM_UTF16_LE = ''
BOM_UTF32 = ''
BOM_UTF32_BE = ''
BOM_UTF32_LE = ''
BOM_UTF8 = ''

class Decoder:
  pass

class Encoder:
  pass

class StreamReader:
  pass

class StreamWriter:
  pass

class EncodedFile:
  def __init__(self, file, data_encoding, file_encoding=None, errors=''):
    return

def lookup(encoding):
  return (Encoder(), Decoder(), StreamReader(), StreamWriter())

def lookup_error(errors):
  return handler

def register(search_function):
  return

def register_error(errors, handler):
  return handler

def open(filename, mode='', encoding=None, errors='strict', buffering=1):
  return

def getencoder(encoding):
  return lookup(encoding).encode

def getdecoder(encoding):
  return lookup(encoding).decode

def getreader(encoding):
  return lookup(encoding).streamreader

def getwriter(encoding):
  return lookup(encoding).streamwriter
