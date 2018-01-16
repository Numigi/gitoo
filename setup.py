#!/usr/bin/env python
# -*- coding: utf-8 -*-

import io
import os
import sys
from shutil import rmtree

from setuptools import find_packages, setup, Command

VERSION = (0, 1, 0)
__version__ = '.'.join(map(str, VERSION))

# Package meta-data.
NAME = 'voodoo'
DESCRIPTION = 'Odoo third party addons installer.'
URL = 'https://github.com/foutoucour/voodoo'
EMAIL = 'kender@gmail.com'
AUTHOR = 'Jordi Riera'

# What packages are required for this module to be executed?
REQUIRED = [
    'GitPython>=2.1.8', 'click>=6.7'
]

here = os.path.abspath(os.path.dirname(__file__))

# Import the README and use it as the long-description.
# Note: this will only work if 'README.rst' is present in your MANIFEST.in file!
with io.open(os.path.join(here, 'README.rst'), encoding='utf-8') as f:
    long_description = '\n' + f.read()

setup(
    name=NAME,
    version=__version__,
    description=DESCRIPTION,
    long_description=long_description,
    author=AUTHOR,
    author_email=EMAIL,
    url=URL,
    packages=find_packages(exclude=('tests',)),
    entry_points='''
        [console_scripts]
        voodoo=voodoo.cli:entry_point
    ''',
    install_requires=REQUIRED,
    include_package_data=True,
    license='MIT',
    classifiers=[
        # Trove classifiers
        # Full list: https://pypi.python.org/pypi?%3Aaction=list_classifiers
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: Implementation :: CPython',
    ],
)