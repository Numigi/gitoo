#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
from setuptools import find_packages, setup
from pip.req import parse_requirements


VERSION = (0, 3, 0)
__version__ = '.'.join(map(str, VERSION))


# parse_requirements() returns generator of pip.req.InstallRequirement objects
dir_path = os.path.dirname(os.path.realpath(__file__))
install_reqs = parse_requirements(os.path.join(dir_path, 'requirements.txt'), session='hack')

# reqs is a list of requirement
REQUIRED = [str(ir.req) for ir in install_reqs]

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

setup(
    name=NAME,
    version=__version__,
    description=DESCRIPTION,
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