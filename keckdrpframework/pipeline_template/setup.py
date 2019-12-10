# !usr/bin/env python
# -*- coding: utf-8 -*-
#
# Licensed under a 3-clause BSD license.

import sys
import os
import glob

from setuptools import setup

# Get some values from the setup.cfg
try:
    from ConfigParser import ConfigParser
except ImportError:
    from configparser import ConfigParser

conf = ConfigParser()
conf.read(['setup.cfg'])
#metadata = dict(conf.items('metadata'))

NAME = 'template'
VERSION = '0.11.1dev'
RELEASE = 'dev' not in VERSION

scripts = [fname for fname in glob.glob(os.path.join('scripts', '*'))
           if os.path.basename(fname) != 'README.rst']

# Define entry points for command-line scripts
entry_points = {'console_scripts': []}


setup(name=NAME,
      provides=NAME,
      version=VERSION,
      license='BSD3',
      description='Template DRP',
      long_description=open('README.txt').read(),
      author='you',
      author_email='you@gmail.com',
      packages=['my_pipeline',],
      scripts=scripts,
      entry_points=entry_points
      )




