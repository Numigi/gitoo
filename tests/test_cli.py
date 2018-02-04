import json
import os
import shutil
import tempfile
import unittest

from src import cli


class TestInstallOne(unittest.TestCase):

    def setUp(self):
        super(TestInstallOne, self).setUp()
        self.func = cli._install_one
        self.repo_url = "https://github.com/OCA/l10n-canada"
        self.branch = "10.0"
        self.commit_rev = "9c1b75a837c0f15e127ee656e871b78db1407505"
        self.destination = tempfile.mkdtemp()
        self.patches = [
            {
                "url": "https://github.com/savoirfairelinux/l10n-canada",
                "branch": "10.0-toponyms_translation",
                "commit": "40176efdbd2acbd4ae70e548af4a077afed11d5d"
            }
        ]

    def tearDown(self):
        super(TestInstallOne, self).tearDown()
        if os.path.exists(self.destination):
            shutil.rmtree(self.destination)

    def test_install(self):
        self.assertFalse(os.listdir(self.destination))
        self.func(
            self.repo_url,
            self.branch,
            self.destination,
            commit=self.commit_rev,
            patches=self.patches
        )

        self.assertTrue(os.listdir(self.destination))

    def test_exclude(self):
        self.func(
            self.repo_url,
            self.branch,
            self.destination,
            commit=self.commit_rev,
            patches=self.patches,
        )
        self.assertTrue(os.path.exists(os.path.join(self.destination, 'setup')))
        shutil.rmtree(self.destination)
        self.destination = tempfile.mkdtemp()
        self.func(
            self.repo_url,
            self.branch,
            self.destination,
            commit=self.commit_rev,
            patches=self.patches,
            exclude_modules=['setup']
        )
        self.assertFalse(os.path.exists(os.path.join(self.destination, 'setup')))


class TestInstallAll(unittest.TestCase):

    def setUp(self):
        super(TestInstallAll, self).setUp()
        self.func = cli._install_all
        _, self.filename = tempfile.mkstemp()
        json_data = [
            {
                "url": "https://github.com/odoo/odoo",
                "branch": "10.0",
                "commit": "ae6037e17acdc66cf28504d9791eb3cd698efaa6",
                "patches": [
                    {
                        "url": "https://github.com/savoirfairelinux/odoo",
                        "branch": "10.0_ddufresne_fix_purchase",
                        "commit": "5f9dd4d2861eeba40cf81e658b99a83d9f88d6e7"
                    }
                ],
                "exclude_modules": ["web_tour"],
                "base": True
            },
            {
                "url": "https://github.com/OCA/l10n-canada",
                "branch": "10.0",
                "commit": "9c1b75a837c0f15e127ee656e871b78db1407505",
                "patches": [
                    {
                        "url": "https://github.com/savoirfairelinux/l10n-canada",
                        "branch": "10.0-toponyms_translation",
                        "commit": "40176efdbd2acbd4ae70e548af4a077afed11d5d"
                    }
                ],
                "exclude_modules": ["setup"]
            }
        ]
        with open(self.filename, 'w') as f:
            json.dump(json_data, f)
        self.destination = tempfile.mkdtemp()

    def tearDown(self):
        super(TestInstallAll, self).tearDown()
        if os.path.exists(self.destination):
            shutil.rmtree(self.destination)

    # def test_install_all(self):
    #     self.assertFalse(os.listdir(self.destination))
    #     self.func(
    #         destination=self.destination,
    #         json_file=self.filename
    #     )
    #     self.assertTrue(os.listdir(self.destination))
