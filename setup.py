#!/usr/bin/env python
# -*- coding: utf-8 -*-

from setuptools import find_packages, setup
from src import manifest

setup(
    name=manifest.name,
    use_scm_version=True,
    setup_requires=['setuptools_scm', 'pytest_runner'],
    description=manifest.description,
    author=manifest.author,
    author_email=manifest.email,
    url=manifest.url,
    packages=find_packages(exclude=('tests',)),
    entry_points='''
        [console_scripts]
        gitoo=src.cli:entry_point
    ''',
    install_requires=[
        'gitpython',
        'click>=7.0',
        'click-didyoumean',
        'crayons',
        'click-help-colors',
        'pyyaml',
        # force the version of pystache as we use private variables of the lib.
        'pystache==0.5.4',
    ],
    tests_require=[
        'pytest',
        'pytest-cov',
        'pytest-random-order',
        'mock',
    ],
    include_package_data=True,
    license='MIT',
    classifiers=[
        # Trove classifiers
        # Full list: https://pypi.python.org/pypi?%3Aaction=list_classifiers
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: Implementation :: CPython',
    ],
)
