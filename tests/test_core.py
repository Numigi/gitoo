from __future__ import print_function, absolute_import
import unittest
import git
import functools
import os

import mock

from src import core


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
        self.includes = ['e3', 'e4']

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

    def test_includes_optional(self):
        inst = self.klass(self.url, self.branch, include_modules=self.includes)
        self.assertEqual(self.includes, inst.include_modules)

    def test_includes_default_value(self):
        inst = self.klass(self.url, self.branch)
        self.assertEqual(None, inst.include_modules)


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


class TestParseUrl(unittest.TestCase):

    def setUp(self):
        super(TestParseUrl, self).setUp()
        self.func = core.parse_url

    def test_no_token(self):
        """
        When the url is a public url
        Then the public url is returned as it.
        """
        url = "https://github.com/OCA/website"
        self.assertEqual(url, self.func(url), msg='no token passed, the url should be the same without change.')

    def test_github_token_provided(self):
        """
        When the url is a private url with the token hard coded in the string
        Then the private url is returned as it
        """
        url_with_token = "https://7777@github.com/numigi/aeroo_reports"
        self.assertEqual(url_with_token, self.func(url_with_token),
                         msg='no token passed, the url should be the same without change.')

    def test_with_env_variable(self):
        """
        Given the environment variable X is set
        When the environment variable X is mentioned in the url, using the mustache syntaxe
        Then the environment variable value is set in the url
        """
        env_variable_name = "GIT_TOKEN"
        env_variable = "6666"
        # use %s syntax here to avoid awkward string with multiple {{ }} just to have the right string
        # it makes it easier to read this way.
        url_template = "https://{{%s}}@github.com/numigi/aeroo_reports" % env_variable_name
        expected = "https://{}@github.com/numigi/aeroo_reports".format(env_variable)

        with mock.patch.dict(os.environ,{env_variable_name:env_variable}):
            self.assertEqual(expected, self.func(url_template))

    def test_with_env_variable_not_defined(self):
        """
        Given the environment variable X is not set
        When the environment variable X is mentioned in the url, using the mustache syntaxe
        Then the system raise a KeyError
        """
        env_variable_name = "GIT_TOKEN"
        url_template = "https://{{%s}}@github.com/numigi/aeroo_reports" % env_variable_name

        with self.assertRaises(KeyError):
            self.func(url_template)
