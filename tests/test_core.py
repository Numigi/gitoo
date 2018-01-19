from __future__ import print_function, absolute_import
import unittest
import git
import functools
import os
from voodoo import core


class TestTempRepo(unittest.TestCase):

    def setUp(self):
        super(TestTempRepo, self).setUp()
        self.repo_url = "https://github.com/pytest-dev/pytest"
        self.branch = "master"
        self.commit = "bd2d0d2c3c9bf92711e5a858e93e46d390dd4229"

        self.func = core.temp_repo
        self.filled = functools.partial(self.func, self.repo_url, self.branch)

    def test_contextManager(self):
        with self.filled() as tmp:
            self.assertTrue(os.path.exists(tmp))
        self.assertFalse(os.path.exists(tmp))

    def test_whenCommitNotGiven_thenWeAreInTheBranch(self):
        """When only the branch is given, no commit, we are then on the branch"""
        with self.filled() as tmp:
            repo = git.Repo(path=tmp)
            self.assertEqual(self.branch, repo.active_branch.name)

    def test_whenCommitGiven_thenWeAreOnTheCommit(self):
        with self.filled(commit=self.commit) as tmp:
            repo = git.Repo(path=tmp)
            self.assertEqual(self.commit, repo.head.commit.hexsha)


class TestAddon(unittest.TestCase):

    def setUp(self):
        super(TestAddon, self).setUp()
        self.klass = core.Addon
        self.url = 'url'
        self.branch = 'branch'
        self.commit = 'commit_rev'
        self.patches = [
            core.Patch(self.url, self.branch, self.commit),
            core.Patch(self.url, self.branch, self.commit),
        ]
        self.excludes = ['e1', 'e2']

    def test_required(self):
        inst = self.klass(self.url, self.branch)
        self.assertEqual(self.url, inst.repo)
        self.assertEqual(self.branch, inst.branch)

    def test_commit_rev_optional(self):
        inst = self.klass(self.url, self.branch, commit=self.commit)
        self.assertEqual(self.commit, inst.commit)

    def test_commit_rev_default_value(self):
        inst = self.klass(self.url, self.branch)
        self.assertEqual('', inst.commit)

    def test_patches_optional(self):
        inst = self.klass(self.url, self.branch, patches=self.patches)
        self.assertEqual(self.patches, inst.patches)

    def test_patches_runtimeError(self):
        with self.assertRaises(RuntimeError):
            self.klass(
                self.url, self.branch, patches={"url": self.url, "branch": self.branch, "commit_rev": self.commit}
            )

    def test_patches_default_value(self):
        inst = self.klass(self.url, self.branch)
        self.assertEqual([], inst.patches)

    def test_excludes_optional(self):
        inst = self.klass(self.url, self.branch, exclude_modules=self.excludes)
        self.assertEqual(self.excludes, inst.exclude_modules)

    def test_excludes_default_value(self):
        inst = self.klass(self.url, self.branch)
        self.assertEqual([], inst.exclude_modules)


class TestPatch(unittest.TestCase):

    def setUp(self):
        super(TestPatch, self).setUp()
        self.klass = core.Patch
        self.url = 'url'
        self.branch = 'branch'
        self.commit_rev = 'commit_rev'

    def test_required(self):
        inst = self.klass(self.url, self.branch, self.commit_rev)
        self.assertEqual(self.url, inst.url)
        self.assertEqual(self.branch, inst.branch)
        self.assertEqual(self.commit_rev, inst.commit)
