# !usr/bin/env python
# -*- coding: utf-8 -*-
#
# Licensed under a 3-clause BSD license.

from setuptools import setup, find_packages

# Get some values from the setup.cfg
try:
    from ConfigParser import ConfigParser
except ImportError:
    from configparser import ConfigParser

conf = ConfigParser()
conf.read(['setup.cfg'])
metadata = dict(conf.items('metadata'))
options = dict(conf.items('options'))

NAME = 'keckdrpframework'
VERSION = '1.0'
RELEASE = 'dev' not in VERSION
AUTHOR = metadata['author']
AUTHOR_EMAIL = metadata['author_email']
LICENSE = metadata['license']
DESCRIPTION = metadata['description']


# scripts = [fname for fname in glob.glob(os.path.join('scripts', '*'))
#            if os.path.basename(fname) != 'README.rst']
scripts = []
# Define entry points for command-line scripts
entry_points = {
    'console_scripts': [
    ]}

setup(name=NAME,
      provides=NAME,
      version=VERSION,
      license=LICENSE,
      description=DESCRIPTION,
      long_description=open('README.rst').read(),
      author=AUTHOR,
      author_email=AUTHOR_EMAIL,
      packages=find_packages(),
      scripts=scripts,
      entry_points=entry_points,
      install_requires=options['install_requires'],
      )
