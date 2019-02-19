#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""This file contains settings to setup the project. It's required by
tox.ini among other files."""
from setuptools import setup, find_packages
from config.settings import __version__

PACKAGES = find_packages(exclude=['tests', 'tests.*'])

setup(
    name='analytical_platform',
    packages=PACKAGES,
    python_requires='>=3.5',
    version=__version__,
    description='Description.',
    long_description='Description',
    author='ggravlingen',
    author_email='no@email.com',
    url='https://github.com/',
    license='Proprietary',
    download_url='url',
)
