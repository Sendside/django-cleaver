#!/usr/bin/env python

# Setuptools is a slightly nicer distribution utility that can create 'eggs'.
from setuptools import setup, find_packages

setup(
    name='django-cleaver',
    author='Kevin Williams',
    author_email='kevin@weblivion.com',
    version='0.2.5',
    license='BSD',
    url='https://github.com/isolationism/django-cleaver',
    download_url='https://github.com/isolationism/django-cleaver/tarball/master',
    description='Integrates CleverCSS with Django with built-in support for franchise customisations',
    packages=find_packages(),
    include_package_data = False,
    install_requires = ['clevercss>=0.2.2.dev'],
)

