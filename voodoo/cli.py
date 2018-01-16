#!/usr/bin/env python2
"""
Command line interface of the tool
"""
from __future__ import print_function, absolute_import

import logging
import click

from voodoo import core

logger = logging.getLogger('voodoo')
logger.setLevel(logging.INFO)


@click.group()
def entry_point():
    pass


@entry_point.command()
@click.argument('repo_url')
@click.argument('branch')
@click.argument('destination')
def install_one(repo_url, branch, destination):
    return core.install_third_party_add_on(repo_url, branch, destination)


@entry_point.command()
@click.option('--json_file', default=None, type=click.Path(), help='The path where the json file is.')
@click.option('--destination', default='', type=click.Path(), help='The path where the add-ons should be installed to.')
def install_all(destination='', json_file=None):
    return core.install_all_third_party_add_ons(destination, json_file)
