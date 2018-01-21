#!/usr/bin/env python2
"""
Command line interface of the tool
"""
from __future__ import print_function, absolute_import

import json
import logging
import os

import click
from voodoo import core

logger = logging.getLogger('voodoo')
logging.basicConfig()
logger.setLevel(logging.INFO)


@click.group()
def entry_point():
    pass


@entry_point.command()
@click.argument('repo_url')
@click.argument('branch')
@click.argument('destination')
@click.option('--base', default=False)
def install_one(repo_url, branch, destination, base=False):
    return _install_one(repo_url, branch, destination, base=base)


@entry_point.command()
@click.option('--json_file', default=None, type=click.Path(), help='The path where the json file is.')
@click.option('--destination', default='', type=click.Path(), help='The path where the add-ons should be installed to.')
def install_all(destination='', json_file=None):
    return _install_all(destination, json_file)


def _install_one(repo_url, branch, destination, commit='', patches=None, exclude_modules=None, base=False):
    """ Install a third party odoo add-on

    :param string repo_url: url of the repo that contains the patch.
    :param string branch: name of the branch to checkout.
    :param string destination: the folder where the add-on should end up at.
    :param string commit: Optional commit rev to checkout to. If mentioned, that take over the branch
    :param list patches: Optional list of patches to apply.
    """
    patches = patches or []
    patches = [core.Patch(**patch) for patch in patches]
    addon_cls = core.Base if base else core.Addon
    addon = addon_cls(repo_url, branch, commit=commit, patches=patches, exclude_modules=exclude_modules)
    addon.install(destination)


def _install_all(destination='', json_file=''):
    """Use the json file to list all the third party Odoo add-ons that will be installed
    and the patches that should be applied.

    :param string destination: the folder where add-ons should end up at.
                               Default: pwd/3rd
    :param string json_file: path to a json file that describe the add-ons to install.
                             Default: pwd/third_party_addons.json
    """
    dir_path = os.path.dirname(os.path.realpath(__file__))
    destination = destination or os.path.join(dir_path, '..', '3rd')
    json_file = json_file or os.path.join(dir_path, '..', "third_party_addons.json")
    with open(json_file, "r") as json_data:
        data = json.load(json_data)
        for addons in data:
            _install_one(
                addons['url'],
                addons['branch'],
                os.path.abspath(destination),
                commit=addons.get('commit'),
                patches=addons.get('patches'),
                exclude_modules=addons.get('excludes'),
                base=addons.get('base'),
            )
