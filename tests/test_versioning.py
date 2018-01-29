"""Test the versionning of the current package.

It reminds to update the version.
"""
import tempfile
import unittest
import git

from voodoo import manifest


class TestVersion(unittest.TestCase):

    def setUp(self):
        super(TestVersion, self).setUp()
        self.current_version = manifest.version

    def test_available_version(self):
        """Check if the current version of the package is already released/tagged."""
        # should have a ssh key installed at this point, either locally or on the CI system.
        url = manifest.url.replace('https://github.com/', 'git@github.com:')
        tmp = tempfile.mkdtemp()
        repo = git.Repo.clone_from(url, tmp)
        tags= [tag.name for tag in repo.tags]
        self.assertNotIn(
            manifest.version, tags,
            msg=(
                "This version {} is already tagged."
                " You need to update {}. Use `git tag` to see the releases.".format(
                    manifest.version, manifest.__file__
                )
            )
        )