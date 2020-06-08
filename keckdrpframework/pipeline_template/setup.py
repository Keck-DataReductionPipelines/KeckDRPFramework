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


# MODIFY THE NAME OF THE PACKAGE to be the one chosen
NAME = 'template'
VERSION = '0.0'
RELEASE = 'dev' not in VERSION

scripts = []

entry_points = {
    'console_scripts': [
        "template_script = pipeline_template.scripts.template_script:main"
    ]
}


# modify the list of packages, to make sure that your package is defined correctly
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




