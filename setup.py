#!/usr/bin/env python
import io
import os
import sys

from setuptools import find_packages, setup


if sys.argv[-1] == 'publish':
    os.system('python setup.py sdist upload')
    os.system('python setup.py bdist_wheel upload')
    sys.exit()


readme = io.open('README.rst', 'r', encoding='utf-8').read()

setup(
    name='magnivore',
    description='Data migration that can be configured using JSON',
    long_description=readme,
    url='https://github.com/wearewhys/magnivore',
    author='Jacopo Cascioli',
    author_email='jacopocascioli@gmail.com',
    license='Apache 2',
    version='0.3.1',
    packages=find_packages(),
    tests_require=[
        'pytest',
        'pytest-mock'
    ],
    setup_requires=['pytest-runner'],
    install_requires=[
        'peewee>=2.8.0',
        'aratrum>=0.2.0',
        'ujson>=1.35',
        'click>=6.7',
    ],
    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Console',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: Apache Software License',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 3',
        'Topic :: Database'
    ],
    entry_points="""
        [console_scripts]
        magnivore=magnivore.Cli:Cli.main
    """
)
