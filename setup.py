# -*- encoding: utf-8 -*-
"""Setupfile for the pingpong package.

Author: Bas Vonk
Date: 2018-09-22
"""

from setuptools import setup

setup(name='pacpong',
      version='1.0.0',
      description='Pingpong competition tools.',
      author='Bas Vonk',
      author_email='sjj.vonk@gmail.com',
      license='MIT',
      classifiers=[
          "Programming Language :: Python :: 3"
      ],
      packages=['pacpong'],
      install_requires=[
          'coverage',
          'gspread',
          'numpy',
          'oauth2client',
          'pycodestyle',
          'pydocstyle',
          'typing',
          'unittest2',
          'pytz'
      ],
      zip_safe=False)
