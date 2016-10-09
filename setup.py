#!/usr/bin/env python

from setuptools import setup

setup(name='broti',
      version='1.0',
      description='A bot for IRC',
      author='Stefan Koch',
      author_email='programming@stefan-koch.name',
      packages=['broti', 'broti.modules', 'broti.providers'],
      install_requires=['irc'],
      entry_points = {
          'console_scripts': ['broti = broti.cmdline:execute'],
      }
)
