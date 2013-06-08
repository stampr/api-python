#!/usr/bin/env python

from __future__ import absolute_import, division, print_function, unicode_literals

import os

try:
    import sphinx
except ImportError:
    print("Install sphinx with: pip install sphinx")
    exit(1)

try:
    from shovel import task
except ImportError:
    print("Install shovel with: pip install shovel")
    exit(1)

'''
Run these tasks via::

    $ shovel docs
    $ shovel release
'''

@task
def docs():
    '''Generate Sphinx documentation'''

    os.system("sphinx-apidoc -o doc stampr")
    os.system("python setup.py build_sphinx")
    print()
    print("HTML documentation generated: build/sphinx/html/index.html")


@task
def release():
    '''Create source distribution.'''

    result = os.system("python setup.py sdist")

    if result == 0:
        print()
        print("Distribution package created in dist/")

