# -*- coding: utf-8 -*-

from setuptools import setup, find_packages

with open('README.rst') as f:
    readme = f.read()

setup(
    name='rec2sqlite',
    version='1.7',
    description='Creates SQLite databases from flat files',
    long_description=readme,
    author='Pravles Redneckoff',
    author_email='pravles@pm.me',
    url='https://pravles.com',
    license='',
    packages=find_packages(exclude=('tests', 'docs'))
)
