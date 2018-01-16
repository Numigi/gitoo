#!/usr/bin/env python2
"""
Core functions
"""
from __future__ import print_function, absolute_import

import json
import subprocess
import os
import tempfile
import shutil
import contextlib
import logging

import git

logger = logging.getLogger('voodoo-core')
logger.setLevel(logging.INFO)


@contextlib.contextmanager
def temp_repo(repo_url, branch, commit_rev=''):
    """ Clone a git repository inside a temporary folder, yield the folder then delete the folder.

    :param string repo_url: url of the repo to clone.
    :param string branch: name of the branch to checkout to.
    :param string commit_rev: Optional commit rev to checkout to. If mentioned, that take over the branch
    :return: yield the path to the temporary folder
    :rtype: string
    """
    tmp_folder = tempfile.mkdtemp()
    git.Repo.clone_from(
        repo_url, tmp_folder, branch=branch
    )
    if commit_rev:
        git_cmd = git.Git(tmp_folder)
        git_cmd.checkout(commit_rev)
    yield tmp_folder
    shutil.rmtree(tmp_folder)


def force_move(source, destination):
    """ Force the move of the source inside the destination even if the destination has already a folder with the
    name inside. In the case, the folder will be replaced.

    :param string source: path of the source to move.
    :param string destination: path of the folder to move the source to.
    """
    destination_folder = os.path.join(destination, os.path.split(source)[-1])
    if os.path.exists(destination_folder):
        shutil.rmtree(destination_folder)
    shutil.move(source, destination)


def apply_patch(folder, repo_url, branch, commit_rev):
    """ Merge code from the given repo url to the git repo contained in the given folder.

    :param string folder: path of the folder where is the git repo cloned at.
    :param string repo_url: url of the repo that contains the patch.
    :param string branch: name of the branch to checkout.
    :param string commit_rev: commit rev to apply
    :raise: RuntimeError if the patch could not be applied.
    """
    logger.info("Apply Patch %s@%s (commit %s)", repo_url, branch, commit_rev)
    remote_name = 'patch'
    commands = [
        "git remote add {} {}".format(remote_name, repo_url),
        "git fetch {} {}".format(remote_name, branch),
        'git merge {} -m "patch"'.format(commit_rev),
        "git remote remove {}".format(remote_name),
    ]
    for command in commands:
        logger.debug("command: %s", command)
        # avoid usage of shell = True
        # see https://docs.openstack.org/bandit/latest/plugins/subprocess_popen_with_shell_equals_true.html
        process = subprocess.Popen(command.split(), stdout=subprocess.PIPE, cwd=folder)
        stream_data = process.communicate()[0]
        logger.debug("Merge stdout: %s (RC %s)", stream_data, process.returncode)
        if process.returncode:
            msg = "Could not apply patch from {}@{}: {}. Error: {}".format(repo_url, branch, command, stream_data)
            logger.error(msg)
            raise RuntimeError(msg)


def install_third_party_add_on(repo_url, branch, destination, commit_rev='', patches=None):
    """ Install a third party odoo add-on

    :param string repo_url: url of the repo that contains the patch.
    :param string branch: name of the branch to checkout.
    :param string destination: the folder where the add-on should end up at.
    :param string commit_rev: Optional commit rev to checkout to. If mentioned, that take over the branch
    :param list patches: Optional list of patches to apply.
    """
    patches = patches or []
    logger.info("Installing %s@%s to %s", repo_url, commit_rev if commit_rev else branch, destination)
    with temp_repo(repo_url, branch, commit_rev) as tmp:
        for patch in patches:
            apply_patch(tmp, patch["url"], patch["branch"], patch["commit"])

        paths = (
            os.path.join(tmp, path) for path in os.listdir(tmp)
        )
        folders = (
            path for path in paths if os.path.isdir(path)
        )
        for folder in folders:
            force_move(folder, destination)


def install_all_third_party_add_ons(destination='', json_file=''):
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
            install_third_party_add_on(
                addons['url'],
                addons['branch'],
                os.path.abspath(destination),
                addons.get('commit'),
                addons.get('patches'),
            )
