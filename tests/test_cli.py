import yaml
import os
import shutil
import tempfile
import unittest

from src import cli


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


class ThirdPartyTestMixin(unittest.TestCase):

    def setUp(self):
        super(ThirdPartyTestMixin, self).setUp()
        self.func = cli._install_all
        _, self.filename = tempfile.mkstemp()
        with open(self.filename, 'w') as f:
            yaml.dump(self._yaml_data, f)
        self.destination = tempfile.mkdtemp()

    def tearDown(self):
        super(ThirdPartyTestMixin, self).tearDown()
        if os.path.exists(self.destination):
            shutil.rmtree(self.destination)


class TestInstallThirdParty(ThirdPartyTestMixin):

    _yaml_data = [
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

    def test_install_all(self):
        self.assertFalse(os.listdir(self.destination))
        self.func(destination=self.destination, conf_file=self.filename)
        self.assertTrue(os.listdir(self.destination))

    def test_destination_folder_does_not_exist(self):
        destination = os.path.join(self.destination, 'addons')
        with self.assertRaises(RuntimeError):
            self.func(destination=destination, conf_file=self.filename)


class TestInstallThirdPartyWithIncludes(ThirdPartyTestMixin):

    _included_modules = ["website_multi_theme", "website_odoo_debranding"]

    _yaml_data = [
        {
            "url": "https://github.com/OCA/website",
            "branch": "11.0",
            "commit": "899a2219d35a259422ce916ba99947108bc3cc3c",
            "includes": _included_modules,
        },
    ]

    def test_install_all(self):
        self.assertFalse(os.listdir(self.destination))
        self.func(destination=self.destination, conf_file=self.filename)
        modules = os.listdir(self.destination)
        self.assertEqual(set(modules), set(self._included_modules))


class TestPatchUsingFile(ThirdPartyTestMixin):

    _patch_name = 'server-tools-sentry-readme.patch'

    _yaml_data = [
        {
            "url": "https://github.com/OCA/server-tools",
            "branch": "11.0",
            "commit": "32291d5b6aed0a9a3400975288fc6bef2cb5f985",
            "patches": [
                {
                    "file": "gitoo-patches/{}".format(_patch_name),
                },
            ]
        },
    ]

    def setUp(self):
        super(TestPatchUsingFile, self).setUp()
        dir_path = os.path.dirname(os.path.realpath(__file__))
        self.patch_file = os.path.join(dir_path, 'patches', self._patch_name)
        self.patches_dir = '/tmp/gitoo-patches'
        os.makedirs(self.patches_dir, exist_ok=True)
        shutil.copy2(self.patch_file, self.patches_dir)

    def tearDown(self):
        super(TestPatchUsingFile, self).tearDown()
        if os.path.exists(self.patch_file):
            shutil.rmtree(self.patches_dir)

    def test_install_all(self):
        self.assertFalse(os.listdir(self.destination))
        self.func(destination=self.destination, conf_file=self.filename)

        readme_file = os.path.join(self.destination, 'sentry', 'README.rst')
        readme_content = open(readme_file, 'r').read()
        self.assertIn('This is a patch.', readme_content)
