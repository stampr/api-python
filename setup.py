#!/usr/bin/env python

# Doesn't like Python3 stuff, so don't include this.
#from __future__ import absolute_import, division, print_function, unicode_literals

from setuptools import setup, find_packages

setup(
    name = "stampr",
    version = "0.1.0",
    url = "https:/github.com/stampr/stampr-python-api",
    description = "A module (with command line application) to access uptimetobot.com API",
    author = "Bil Bas",
    author_email = "bil.bas.dev@gmail.com",
    maintainer = "Cory Mawhorter",
    #maintainer_email = "",
    license = "MIT License",
    install_requires = [
        "requests>=1.2.0",
        "certifi>=0.0.8",
        "python-dateutil>=2.1",
    ],
    packages = find_packages(),
    #include_package_data=True,
    zip_safe=True,
    classifiers=[
        'Development Status :: 4 - Beta',
        #'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Natural Language :: English',
        'Operating System :: MacOS :: MacOS X',
        'Operating System :: Microsoft :: Windows',
        'Operating System :: POSIX',
        'Programming Language :: Python',
    ],
)