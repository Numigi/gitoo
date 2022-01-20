from __future__ import print_function, absolute_import, unicode_literals
import os
import logging
import subprocess
import tempfile
import shutil
import contextlib

import pystache
from pystache.parser import _EscapeNode  # pylint: disable=protected-access
import git

logger = logging.getLogger('gitoo-definition')
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
    if not os.path.exists(destination):
        raise RuntimeError(
            'The code could not be moved to {destination} '
            'because the folder does not exist'.format(destination=destination))

    destination_folder = os.path.join(destination, os.path.split(source)[-1])

    if os.path.exists(destination_folder):
        shutil.rmtree(destination_folder)
    shutil.move(source, destination)


class Addon(object):
    """ Struct define the requirements of an add-on for src."""

    def __init__(
        self, url, branch, commit='', patches=None,
        exclude_modules=None, include_modules=None,
        lang='',
    ):
        """ Init

        :param string url: url where the add-on lives.
        :param string branch: the branch to check out.
        :param string commit: Optional commit sha.
        :param list patches: list of PatchDefinition
        :param list exclude_modules: list of name of modules to exclude.
        :param list include_modules: list of name of modules to include.
        """
        self.repo = parse_url(url)
        self.branch = branch
        self.commit = commit
        self.patches = patches or []
        if not all(isinstance(patch, (Patch, FilePatch)) for patch in self.patches):
            raise RuntimeError("Patches should be defined using Patch or FilePatch object.")
        self.exclude_modules = exclude_modules or []
        self.include_modules = include_modules
        self.languages = lang.split(',') if lang else []

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
            self._delete_unrequired_languages(tmp)
            self._move_modules(tmp, destination)

    def _apply_patches(self, temp_repo):
        """Apply patches to the repository.

        :param string temp_repo: the folder containing the code.
        """
        for patch in self.patches:
            patch.apply(temp_repo)

    def _delete_unrequired_languages(self, temp_repo):
        if not self.languages:
            return

        for directory, file_name in self._iter_po_files(temp_repo):
            lang = file_name.split('.')[0]
            if lang not in self.languages:
                file_path = os.path.join(directory, file_name)
                os.remove(file_path)

    def _iter_po_files(self, temp_repo):
        for i18n_folder in self._iter_i18n_folders(temp_repo):
            po_files = os.listdir(i18n_folder)
            for file_name in po_files:
                yield i18n_folder, file_name

    def _iter_i18n_folders(self, temp_repo):
        for folder in self._iter_included_modules(temp_repo):
            i18n_folder = folder + '/i18n'
            if os.path.isdir(i18n_folder):
                yield i18n_folder

    def _move_modules(self, temp_repo, destination):
        """Move modules from the temp directory to the destination.

        :param string temp_repo: the folder containing the code.
        :param string destination: the folder where the add-on should end up at.
        """
        for folder in self._iter_included_modules(temp_repo):
            force_move(folder, destination)

    def _iter_included_modules(self, temp_repo):
        for path in self._iter_modules(temp_repo):
            module_name = path.split("/")[-1]
            if self._is_module_included(module_name):
                yield path

    @staticmethod
    def _iter_modules(temp_repo):
        yield from iter_module_folders(temp_repo)

    def _is_module_included(self, module):
        """Evaluate if the module must be included in the Odoo addons.

        :param string module: the name of the module
        :rtype: bool
        """
        if module in self.exclude_modules:
            return False

        if self.include_modules is None:
            return True

        return module in self.include_modules


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

        for folder in iter_module_folders(tmp_addons):
            force_move(folder, tmp_odoo_addons)

        tmp_odoo = os.path.join(temp_repo, 'odoo')
        force_move(tmp_odoo, destination)

    @staticmethod
    def _iter_modules(temp_repo):
        for directory in ('addons', 'odoo/addons'):
            directory_path = os.path.join(temp_repo, directory)
            yield from iter_module_folders(directory_path)


def _run_command_inside_folder(command, folder):
    """Run a command inside the given folder.

    :param string command: the command to execute.
    :param string folder: the folder where to execute the command.
    :return: the return code of the process.
    :rtype: Tuple[int, str]
    """
    logger.debug("command: %s", command)
    # avoid usage of shell = True
    # see https://docs.openstack.org/bandit/latest/plugins/subprocess_popen_with_shell_equals_true.html
    process = subprocess.Popen(command.split(), stdout=subprocess.PIPE, cwd=folder)
    stream_data = process.communicate()[0]
    logger.debug("%s stdout: %s (RC %s)", command, stream_data, process.returncode)
    return process.returncode, stream_data


class Patch(object):

    def __init__(self, url, branch, commit):
        """ Init

        :param string url: url where the add-on lives.
        :param string branch: the branch to check out.
        :param string commit: Optional commit sha.
        """
        self.url = parse_url(url)
        self.branch = branch
        self.commit = commit

    def apply(self, folder):
        """ Merge code from the given repo url to the git repo contained in the given folder.

        :param string folder: path of the folder where is the git repo cloned at.
        :raise: RuntimeError if the patch could not be applied.
        """
        logger.info("Apply Patch %s@%s (commit %s)", self.url, self.branch, self.commit)
        remote_name = 'patch'
        commands = [
            "git remote add {} {}".format(remote_name, self.url),
            "git fetch {} {}".format(remote_name, self.branch),
            'git merge {} -m "patch"'.format(self.commit),
            "git remote remove {}".format(remote_name),
        ]
        for command in commands:
            return_code, stream_data = _run_command_inside_folder(command, folder)
            if return_code:
                msg = "Could not apply patch from {}@{}: {}. Error: {}".format(
                    self.url, self.branch, command, stream_data)
                logger.error(msg)
                raise RuntimeError(msg)


class FilePatch(object):

    def __init__(self, file, work_directory):
        """ Init

        :param string file: the relative path to the patch file.
        :param string work_directory: the path to the directory of the yaml file.
        """
        self.file_path = os.path.join(work_directory, file)

    def apply(self, folder):
        """Apply a patch from a git patch file.

        :param string folder: path of the folder where is the git repo cloned at.
        :raise: RuntimeError if the patch could not be applied.
        """
        logger.info("Apply Patch File %s", self.file_path)
        command = "git apply {}".format(self.file_path)
        return_code, stream_data = _run_command_inside_folder(command, folder)

        if return_code:
            msg = "Could not apply patch file at {}. Error: {}".format(self.file_path, stream_data)
            logger.error(msg)
            raise RuntimeError(msg)


def iter_module_folders(directory):
    for file in os.listdir(directory):
        file_path = os.path.join(directory, file)
        if _is_odoo_module(file_path):
            yield file_path


def _is_odoo_module(file_path):
    return (
        os.path.isdir(file_path) and
        '__manifest__.py' in os.listdir(file_path)
    )


def parse_url(url):
    """ Parse the given url and update it with environment value if required.

    :param basestring url:
    :rtype: basestring
    :raise: KeyError if environment variable is needed but not found.
    """
    # the url has to be a unicode by pystache's design, but the unicode concept has been rewamped in py3
    # we use a try except to make the code compatible with py2 and py3
    try:
        url = unicode(url)
    except NameError:
        url = url

    parsed = pystache.parse(url)
    # pylint: disable=protected-access
    variables = (element.key for element in parsed._parse_tree if isinstance(element, _EscapeNode))
    return pystache.render(url, {variable: os.environ[variable] for variable in variables})
