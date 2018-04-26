# Gitoo

A library to manage odoo add-ons.

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

## Commands
gitoo contains the following command:

* [Install All](#install_all)

## <a name="install_all"></a> Install All

A tool for creating backups of a database.

```bash
gitoo install_all --conf_file gitoo.yml --destination /mnt/extra-addons
```

* The parameter `--conf_file` expects a path to a [config file](#gitoo_config_file).
The parameter defaults to `./third_party_addons.yaml`
* The parameter `--destination` expects the path where the add-ons should be copied to.
The parameter defaults to `./3rd/`


## <a name="git_config_file"></a>Config File

Gitoo uses a config file, in yml, to know what add-ons should be downloaded and how.

A typical config file would looks like:
``` yaml
- url: https://github.com/odoo/odoo
  branch: "11.0"
  base: true
  
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

* The first section downloads odoo from the branch 11.0. The argument base informs gitoo that the repo is actually 
the code of the application, not a simple add-on
* The second section downloads the code of the repo website from the branch 11.0. It also forces
to be at a precise commit
* The third section shows how to apply patches

