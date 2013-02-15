# Makefile for pyntch

PACKAGE=pyntch
PREFIX=/usr/local

SVN=svn
RM=rm -f
CP=cp -f
PYTHON=python

VERSION=`$(PYTHON) $(PACKAGE)/__init__.py`
DISTFILE=$(PACKAGE)-$(VERSION).tar.gz
TCHECKER=tools/tchecker.py

all:

install:
	$(PYTHON) setup.py install --prefix=$(PREFIX)

clean:
	-$(PYTHON) setup.py clean
	-$(RM) -r build dist selfcheck.xml
	-cd $(PACKAGE) && $(MAKE) clean
	-cd tools && $(MAKE) clean

commit: clean
	$(SVN) commit

check:
	cd test && $(MAKE) check

selfcheck:
	PYTHONPATH=. $(PYTHON) $(TCHECKER) -t xml $(TCHECKER) > selfcheck.xml

sdist: clean
	$(PYTHON) setup.py sdist

register: clean
	$(PYTHON) setup.py sdist upload register

WEBDIR=$$HOME/Site/unixuser.org/python/$(PACKAGE)
publish: sdist
	cp dist/$(DISTFILE) $(WEBDIR)/
	cp docs/index.html docs/*.png $(WEBDIR)/
