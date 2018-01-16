import functools
import unittest

import os

import git

from voodoo import core

class TestTempRepo(unittest.TestCase):

    def setUp(self):
        super(TestTempRepo, self).setUp()
        self.repo_url = "https://github.com/pytest-dev/pytest"
        self.branch = "master"
        self.commit_rev = "bd2d0d2c3c9bf92711e5a858e93e46d390dd4229"

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
        with self.filled(commit_rev=self.commit_rev) as tmp:
            repo = git.Repo(path=tmp)
            self.assertEqual(self.commit_rev, repo.head.commit.hexsha)
