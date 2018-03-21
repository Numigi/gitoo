import yaml
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


class TestInstallBase(unittest.TestCase):

    def setUp(self):
        super(TestInstallBase, self).setUp()
        self.func = cli._install_all
        _, self.filename = tempfile.mkstemp()
        yaml_data = [
            {
                "url": "https://github.com/odoo/odoo",
                "branch": "10.0",
                "commit": "1ad8867deea179e3548f8f7619fd1bd11d1446ae",
                "patches": [
                    {
                        "url": "https://github.com/ddufresne/odoo",
                        "branch": "10.0-ddufresne-fix_aged_partner_balance",
                        "commit": "97929246ca0c7df24b4d46adc27d440712687b5a"
                    },
                ],
                "exclude_modules": ["web_tour"],
                "base": True
            },
        ]
        with open(self.filename, 'w') as f:
            yaml.dump(yaml_data, f)
        self.destination = tempfile.mkdtemp()

    def tearDown(self):
        super(TestInstallBase, self).tearDown()
        if os.path.exists(self.destination):
            shutil.rmtree(self.destination)

    def test_install_all(self):
        self.assertFalse(os.listdir(self.destination))
        self.func(
            destination=self.destination,
            conf_file=self.filename
        )
        self.assertTrue(os.listdir(self.destination))


class TestInstallThirdParty(unittest.TestCase):

    def setUp(self):
        super(TestInstallThirdParty, self).setUp()
        self.func = cli._install_all
        _, self.filename = tempfile.mkstemp()
        yaml_data = [
            {
                "url": "https://github.com/OCA/server-tools",
                "branch": "11.0",
                "commit": "32291d5b6aed0a9a3400975288fc6bef2cb5f985",
                "patches": [
                    {
                        "url": "https://github.com/ddufresne/server-tools",
                        "branch": "11.0-mig-super_calendar",
                        "commit": "34e67cab64250de60fa4e1c24cae3fbc3962a250"
                    },
                ]
            },
            {
                "url": "https://github.com/OCA/website",
                "branch": "11.0",
                "commit": "899a2219d35a259422ce916ba99947108bc3cc3c",
            },
        ]
        with open(self.filename, 'w') as f:
            yaml.dump(yaml_data, f)
        self.destination = tempfile.mkdtemp()

    def tearDown(self):
        super(TestInstallThirdParty, self).tearDown()
        if os.path.exists(self.destination):
            shutil.rmtree(self.destination)

    def test_install_all(self):
        self.assertFalse(os.listdir(self.destination))
        self.func(destination=self.destination, conf_file=self.filename)
        self.assertTrue(os.listdir(self.destination))

    def test_destination_folder_does_not_exist(self):
        destination = os.path.join(self.destination, 'addons')
        with self.assertRaises(RuntimeError):
            self.func(destination=destination, conf_file=self.filename)
