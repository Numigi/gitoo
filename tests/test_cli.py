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
                "base": True,
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
            conf_file=self.filename,
            lang='fr',
        )
        self.assertTrue(os.listdir(self.destination))

        # Test lang parameter
        base_i18n_files = os.listdir(self.destination + "/odoo/addons/base/i18n")
        self.assertEqual(base_i18n_files, ["fr.po"])
        account_i18n_files = os.listdir(self.destination + "/odoo/addons/account/i18n")
        self.assertEqual(account_i18n_files, ["fr.po"])


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

    def test_git_folder_excluded(self):
        self.func(destination=self.destination, conf_file=self.filename)
        git_folder = os.path.join(self.destination, '.git')
        self.assertFalse(os.path.exists(git_folder))

    def test_install_fr_lang_only(self):
        self.func(destination=self.destination, conf_file=self.filename, lang="fr")
        available_files = os.listdir(self.destination + "/auditlog/i18n")
        self.assertEqual(available_files, ["fr.po"])

    def test_install_two_languages(self):
        self.func(destination=self.destination, conf_file=self.filename, lang="fr,es")
        available_files = os.listdir(self.destination + "/auditlog/i18n")
        available_files.sort()
        self.assertEqual(available_files, ["es.po", "fr.po"])

    def test_install_all_languages_by_default(self):
        self.func(destination=self.destination, conf_file=self.filename, lang="")
        available_files = os.listdir(self.destination + "/auditlog/i18n")
        self.assertIn("fr.po", available_files)


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

        self.func = cli._install_all

        self.working_dir = tempfile.mkdtemp()

        # Add the yaml conf to the working directory
        self.yaml_filename = os.path.join(self.working_dir, 'gitoo.yml')
        with open(self.yaml_filename, 'w') as f:
            yaml.dump(self._yaml_data, f)

        # Copy the patch files to the working directory
        dir_path = os.path.dirname(os.path.realpath(__file__))
        patch_file = os.path.join(dir_path, 'patches', self._patch_name)
        patches_dir = os.path.join(self.working_dir, 'gitoo-patches')
        os.makedirs(patches_dir)
        shutil.copy2(patch_file, patches_dir)

        # Create the destination directory
        self.destination = tempfile.mkdtemp()

    def tearDown(self):
        super(TestPatchUsingFile, self).tearDown()

        if os.path.exists(self.working_dir):
            shutil.rmtree(self.working_dir)

        if os.path.exists(self.destination):
            shutil.rmtree(self.destination)

    def test_install_all(self):
        self.assertFalse(os.listdir(self.destination))
        self.func(destination=self.destination, conf_file=self.yaml_filename)

        readme_file = os.path.join(self.destination, 'sentry', 'README.rst')
        readme_content = open(readme_file, 'r').read()
        self.assertIn('This is a patch.', readme_content)
