
from setuptools import find_packages, setup

setup(
    name='gitoo',
    use_scm_version=True,
    setup_requires=['setuptools_scm', 'pytest_runner'],
    description='Odoo third party addons installer.',
    author='numigi',
    author_email='contact@numigi.com',
    url='https://github.com/numigi/gitoo',
    packages=find_packages(exclude=('tests',)),
    entry_points='''
        [console_scripts]
        gitoo=gitoo.cli:entry_point
    ''',
    install_requires=[
        'gitpython',
        'click',
        'click-didyoumean',
        'crayons',
        'click-help-colors',
        'pyyaml',
        'pystache',
    ],
    tests_require=[
        'pytest',
        'pytest-cov',
        'pytest-random-order',
        'mock',
    ],
    include_package_data=True,
    license='MIT',
    classifiers=[
        # Trove classifiers
        # Full list: https://pypi.python.org/pypi?%3Aaction=list_classifiers
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: Implementation :: CPython',
    ],
)
