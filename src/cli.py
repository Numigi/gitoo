#!/usr/bin/env python2
"""
Command line interface of the tool
"""
from __future__ import print_function, absolute_import

import yaml
import logging
import os

import click
from click_didyoumean import DYMMixin
from click_help_colors import HelpColorsGroup

from src import core

logger = logging.getLogger('gitoo')
logging.basicConfig()
logger.setLevel(logging.INFO)


class AllGroup(DYMMixin, HelpColorsGroup, click.Group):  # pylint: disable=too-many-public-methods
    pass


@click.group(
    cls=AllGroup,
    help_headers_color='yellow',
    help_options_color='green'
    )
@click.version_option()
def entry_point():
    pass


@entry_point.command()
@click.option('--conf_file', default=None, type=click.Path(), help='The path where the conf file is.')
@click.option('--destination', default='', type=click.Path(), help='The path where the add-ons should be installed to.')
def install_all(destination='', conf_file=None):
    return _install_all(destination, conf_file)


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


def _install_all(destination='', conf_file=''):
    """Use the conf file to list all the third party Odoo add-ons that will be installed
    and the patches that should be applied.

    :param string destination: the folder where add-ons should end up at.
                               Default: pwd/3rd
    :param string conf_file: path to a conf file that describe the add-ons to install.
                             Default: pwd/third_party_addons.yaml
    """
    dir_path = os.path.dirname(os.path.realpath(__file__))
    destination = destination or os.path.join(dir_path, '..', '3rd')
    conf_file = conf_file or os.path.join(dir_path, '..', "third_party_addons.yaml")
    with open(conf_file, "r") as conf_data:
        data = yaml.load(conf_data)
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
