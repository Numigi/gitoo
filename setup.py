#!/usr/bin/env python
# -*- coding: utf-8 -*-

from setuptools import find_packages, setup
from voodoo import manifest

try:
    from pipenv.project import Project
    from pipenv.utils import convert_deps_to_pip
except ImportError:
    raise ImportError(
        "`pipenv` is required to install {}. Please run `pip install pipenv` then retry.".format(manifest.name)
    )

pfile = Project(chdir=False).parsed_pipfile
install_reqs = convert_deps_to_pip(pfile['packages'], r=False)

setup(
    name=manifest.name,
    version=manifest.version,
    description=manifest.description,
    author=manifest.author,
    author_email=manifest.email,
    url=manifest.url,
    packages=find_packages(exclude=('tests',)),
    entry_points='''
        [console_scripts]
        voodoo=voodoo.cli:entry_point
    ''',
    install_requires=install_reqs,
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
        'Programming Language :: Python :: Implementation :: CPython',
    ],
)
