from __future__ import print_function, absolute_import
import os
import logging
import subprocess
import tempfile
import shutil
import contextlib
import git

logger = logging.getLogger('src-definition')
logger.setLevel(logging.INFO)


@contextlib.contextmanager
def temp_repo(url, branch, commit=''):
    """ Clone a git repository inside a temporary folder, yield the folder then delete the folder.

    :param string url: url of the repo to clone.
    :param string branch: name of the branch to checkout to.
    :param string commit: Optional commit rev to checkout to. If mentioned, that take over the branch
    :return: yield the path to the temporary folder
    :rtype: string
    """
    tmp_folder = tempfile.mkdtemp()
    git.Repo.clone_from(
        url, tmp_folder, branch=branch
    )
    if commit:
        git_cmd = git.Git(tmp_folder)
        git_cmd.checkout(commit)
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


class Addon(object):
    """ Struct define the requirements of an add-on for src."""

    def __init__(self, url, branch, commit='', patches=None, exclude_modules=None):
        """ Init

        :param string url: url where the add-on lives.
        :param string branch: the branch to check out.
        :param string commit: Optional commit sha.
        :param list patches: list of PatchDefinition
        :param list exclude_modules: list of name of modules to exclude.
        """
        self.repo = url
        self.branch = branch
        self.commit = commit
        self.patches = patches or []
        if not all(isinstance(patch, Patch) for patch in self.patches):
            raise RuntimeError("Patches should be defined using Patch object.")
        exclude_modules = exclude_modules or []
        self.exclude_modules = exclude_modules or []

    def install(self, destination):
        """ Install a third party odoo add-on

        :param string destination: the folder where the add-on should end up at.
        """
        logger.info(
            "Installing %s@%s to %s",
            self.repo, self.commit if self.commit else self.branch, destination
        )
        with temp_repo(self.repo, self.branch, self.commit) as tmp:
            self._apply_patches(tmp)
            self._move_modules(tmp, destination)

    def _apply_patches(self, temp_repo):
        """Apply patches to the repository.

        :param string temp_repo: the folder containing the code.
        """
        for patch in self.patches:
            patch.apply(temp_repo)

    def _move_modules(self, temp_repo, destination):
        """Move modules froom the temp directory to the destination.

        :param string temp_repo: the folder containing the code.
        :param string destination: the folder where the add-on should end up at.
        """
        folders = self._get_module_folders(temp_repo)
        for folder in folders:
            force_move(folder, destination)

    def _get_module_folders(self, temp_repo):
        """Get a list of module paths contained in a temp directory.

        :param string temp_repo: the folder containing the modules.
        """
        paths = (
            os.path.join(temp_repo, path) for path in os.listdir(temp_repo)
            if path not in self.exclude_modules
        )
        return (path for path in paths if os.path.isdir(path))


class Base(Addon):
    """ Struct define the odoo base repository for src."""

    def _move_modules(self, temp_repo, destination):
        """Move odoo modules from the temp directory to the destination.

        This step is different from a standard repository. In the base code
        of Odoo, the modules are contained in a addons folder at the root
        of the git repository. However, when deploying the application,
        those modules are placed inside the folder odoo/addons.

        1- Move modules from addons/ to odoo/addons/ (with the base module).
        2- Move the whole odoo folder to the destination location.
        """
        tmp_addons = os.path.join(temp_repo, 'addons')
        tmp_odoo_addons = os.path.join(temp_repo, 'odoo/addons')
        folders = self._get_module_folders(tmp_addons)
        for folder in folders:
            force_move(folder, tmp_odoo_addons)

        tmp_odoo = os.path.join(temp_repo, 'odoo')
        force_move(tmp_odoo, destination)


class Patch(object):

    def __init__(self, url, branch, commit=None):
        """ Init

        :param string url: url where the add-on lives.
        :param string branch: the branch to check out.
        :param string commit: Optional commit sha.
        """
        self.url = url
        self.branch = branch
        self.commit = commit

    def apply(self, folder):
        """ Merge code from the given repo url to the git repo contained in the given folder.

        :param string folder: path of the folder where is the git repo cloned at.
        :raise: RuntimeError if the patch could not be applied.
        """
        remote_name = 'patch'
        commit = self.commit or "%s/%s" % (remote_name, self.branch)
        logger.info("Apply Patch %s@%s (commit %s)", self.url, self.branch, commit)
        commands = [
            "git remote add {} {}".format(remote_name, self.url),
            "git fetch {} {}".format(remote_name, self.branch),
            'git merge {} -m "patch"'.format(commit),
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
                msg = "Could not apply patch from {}@{}: {}. Error: {}".format(self.url, self.branch, command, stream_data)
                logger.error(msg)
                raise RuntimeError(msg)
