"""
mgtoolkit: metagraph implementation tool

Note that "python setup.py test" invokes pytest on the package. With appropriately
configured setup.cfg, this will check both xxx_test modules and docstrings.

Copyright 2017, dinesha ranathunga.
Licensed under MIT.
"""
# -*- coding: utf-8 -*-

import sys
from setuptools import setup, find_packages
from setuptools.command.test import test as test_command

if sys.version_info[:2] != (2, 7):
    print("mgtoolkit requires Python 2.7 (%d.%d detected)." %
          sys.version_info[:2])
    sys.exit(-1)


# This is a plug-in for setuptools that will invoke py.test
# when you run python setup.py test
class PyTest(test_command):
    # noinspection PyAttributeOutsideInit
    def finalize_options(self):
        test_command.finalize_options(self)
        self.test_args = []
        self.test_suite = True

    def run_tests(self):
        import pytest  # import here, because outside the required eggs aren't loaded yet
        sys.exit(pytest.main(self.test_args))

with open('README.rst') as readme_file:
    readme = readme_file.read()

with open('HISTORY.rst') as history_file:
    history = history_file.read()

requirements = [
    'Click>=6.0',
    'configobj==4.7.0',
    'pytest==2.7.0',
    'numpy==1.10.2'
]

# noinspection PyPep8
setup(
    name='mgtoolkit',
    version='1.0.1',
    description="This is a Python package for implementing metagraphss.",
    long_description=readme + '\n\n' + history,
    author="Dinesha Ranathunga",
    author_email='mgtkhelp@gmail.com',
    url='https://github.com/dinesharanathunga/mgtoolkit',
    packages=[
        'mgtoolkit',
    ],
    package_dir={'mgtoolkit':
                 'mgtoolkit'},

    include_package_data=True,
    install_requires=requirements,
    license="MIT license",
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: MacOS :: MacOS X',
        'Operating System :: POSIX :: Linux',
        'Topic :: System :: Networking',
        'Topic :: Scientific/Engineering :: Mathematics',
        'Programming Language :: Python :: 2.7',
        'Natural Language :: English'
    ],

    keywords="mgtoolkit, metagraph implementation, policy analysis",
    zip_safe=True,
    download_url = 'http://pypi.python.org/pypi/mgtoolkit',
    tests_require=['pytest'],

    entry_points={
        'console_scripts': [
            'mgtoolkit = mgtoolkit.console_script:console_entry',
        ],
    }

)


