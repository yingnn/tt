#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""The setup script."""

from setuptools import setup, find_packages

import tushare_easy

with open('README.rst') as readme_file:
    readme = readme_file.read()

with open('HISTORY.rst') as history_file:
    history = history_file.read()

requirements = [
    'arrow',
    'unipath',
    'pandas',
    'lxml',
    'tushare',
]

setup_requirements = [
    'lxml',
    'pandas',
]

test_requirements = [
    'flake8',
    'tox',
]

setup(
    name='tushare_easy',
    version=tushare_easy.__version__,
    description='make tushare easyer',
    long_description=readme + '\n\n' + history,
    author='yingnn',
    author_email='yingnn@live.cn',
    url='https://github.com/yingnn/tushare_easy',
    packages=find_packages(include=['tushare_easy']),
    include_package_data=True,
    install_requires=requirements,
    license="MIT license",
    zip_safe=False,
    keywords='tushare_easy, tushare',
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Natural Language :: English',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3.3',
    ],
    test_suite='tests',
    tests_require=test_requirements,
    setup_requires=setup_requirements,
    scripts = ['scripts/tushare_easy'], 
)
