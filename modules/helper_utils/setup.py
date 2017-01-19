#!/usr/bin/env python

from distutils.core import setup

setup(name = 'Helper tools',
      version = '1.0',
      description = 'Blender Python helper utilities',
      author = 'Israel Jacquez',
      author_email = 'mrkotfw@gmail.com',
      url = 'https://github.com/ijacquez/blender-tools',
      packages = ['helper_utils'],
      package_dir = {
          'helper_utils': 'lib'
      })
