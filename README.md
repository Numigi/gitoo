# Gitoo

A library to gather odoo add-ons from git repositories.

## Services
Service|Status
:------|:----
Circleci|[![CircleCI](https://circleci.com/gh/Numigi/gitoo.svg?style=svg&circle-token=31993bf8a187dc04f276574da06879c902ae979b)](https://circleci.com/gh/Numigi/gitoo)
Codacy|[![Codacy Badge](https://api.codacy.com/project/badge/Grade/b83d84af2ad74719a097dbe0368ef2fd)](https://www.codacy.com/app/numigi/gitoo?utm_source=github.com&amp;utm_medium=referral&amp;utm_content=Numigi/gitoo&amp;utm_campaign=Badge_Grade)
Coverage|[![Codacy Badge](https://api.codacy.com/project/badge/Coverage/b83d84af2ad74719a097dbe0368ef2fd)](https://www.codacy.com/app/numigi/gitoo?utm_source=github.com&utm_medium=referral&utm_content=Numigi/gitoo&utm_campaign=Badge_Coverage)

## Abstract 
Gitoo downloads the add-ons from the given git repository and place them in the given folder.

During the process, only the folders of the add-on survive of the final move.
Elements like README, setup.py or even the folder .git are excluded from the move.
It keeps the folder light.

At [Numigi](www.numigi.com), gitoo is used to populate the dockers with the wanted odoo addons.

## Why Gitoo?

Gitoo is one of the first tools developped at Numigi.

It is simple to use and completely decoupled from anything other than gathering Odoo modules.

Before we decided to develop and maintain our own tool, we looked at what was used by the other integrators.
Here are the main options we found in the community:

### pip

``pip`` is an awesome tool for managing python dependencies.

People from OCA figured an easy way to integrate Odoo modules with setuptools.
However, this requires all third-party-addons used in a project to have a setup.py file for this setup to be cohesive.

Even the source code of Odoo is incompatible with pip.
This makes the ``managing python dependencies`` argument for pip questionable.

### git-aggregator

Gitoo was inspired by [git-aggregator](https://github.com/acsone/git-aggregator).

However, there is a major difference between both tools.
Gitoo does not use any kind of cache.

It is specifically intended to build container images.
After the gitoo command is ran, the git history is removed.
This allows to make our images as small as possible.

git-aggregator mitigates this issue with shallow clones. This reduces disk space and bandwidth usage.

Bandwidth has never been an issue (at Numigi) for building our images.
For this reason, cloning the whole repo and removing the git history is a better strategy.
It makes the process and the configuration simpler.

## Commands
gitoo contains the following command:

* [Install All](#install_all)

## <a name="install_all"></a> Install All

Install all modules from the given config file.

```bash
gitoo install_all --conf_file gitoo.yml --destination /mnt/extra-addons
```

* The parameter `--conf_file` expects a path to a [config file](#gitoo_config_file).
The parameter defaults to `./third_party_addons.yaml`
* The parameter `--destination` expects the path where the add-ons should be copied to.
The parameter defaults to `./3rd/`

## <a name="git_config_file"></a>Config File

Gitoo uses a config file, in yml, to know what add-ons should be downloaded and how.

### Download odoo add-ons

A typical config file to get odoo add-ons would look like:

``` yaml
- url: https://github.com/OCA/website
  branch: 11.0
  commit: 899a2219d35a259422ce916ba99947108bc3cc3c

- url: https://github.com/OCA/hr
  branch: 11.0
  commit: 0e72182eab23438edf444f4aae3a808d10784082
  patches:
    - url: https://github.com/Numigi/odoo-hr
      branch: 11.0-mig-hr_experience
      commit: 4af0fc7c353864b573dc4543c2f8ae59d168ba69
```

* The first section downloads the code of the repo website from the branch 11.0. It also forces
to be at a precise commit.
* The second section shows how to apply patches

### Applying Patch From File

To apply a patch directly from a .patch file instead of a git branch, you may do as follow:

``` yaml
- url: https://github.com/OCA/hr
  branch: 11.0
  commit: 0e72182eab23438edf444f4aae3a808d10784082
  patches:
    - file: relative/path/to/first.patch
    - file: relative/path/to/second.patch
```

### Special case of Odoo source code**

Gitoo allows to manage the source code of odoo almost like any other code:

``` yaml
- url: https://github.com/odoo/odoo
  branch: "11.0"
  base: true
```
The code downloads odoo from the branch 11.0.
The argument base informs gitoo that the repo is actually the code of the application, not a simple add-on.

This allows gitoo to apply specifc logic related to the structure of the [Odoo source code](https://github.com/odoo/odoo).

Here is an example of command to install the Odoo source code using gitoo:

```bash
export DIST_PACKAGES=/usr/lib/python3/dist-packages/
gitoo install-all --conf_file ./gitoo.yml --destination "${DIST_PACKAGES}"
```

In this example, all modules from the repository will be moved to ``${DIST_PACKAGES}/odoo/addons``.
This includes the modules ``base`` as well as ``account``, ``analytic``, ``hr`` and so on.

### Include Specific Modules

Gitoo allows to specify which modules to import from a repository.

The following config usess ``includes`` to install 2 modules from OCA/hr.

``` yaml
- url: https://github.com/OCA/hr
  branch: 11.0
  includes:
    - hr_experience
    - hr_family
```

Any other module is automatically discarded by gitoo.

### Exclude Specific Modules

It is also possible to exclude specific modules from a repository.
This can be useful when most modules from a repository are trusted and few modules have major issues.

``` yaml
- url: https://github.com/someorganization/somerepo
  branch: 11.0
  excludes:
    - untrusted_module_1
    - untrusted_module_2
```

This config will install all modules except ``untrusted_module_1`` and ``untrusted_module_2``.

### Include Only Specific Languages

It is possible to specify to gitoo a list of languages to include in the i18n folder.

This is done with the option ``--lang``. It accepts a list of language codes separated with commas.

```bash
gitoo install-all ... --lang fr,fr_CA,es
```

This allows to build lighter docker images, because unnecessary po files are excluded.

By default, for retro-compatibility, all languages are included.
