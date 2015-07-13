#!/usr/bin/env python
# Copyright (c) 2013, Digium, Inc.
# Copyright (c) 2014-2015, Yelp, Inc.

import os

from setuptools import setup

import bravado_core

setup(
    name="bravado-core",
    version=bravado_core.version,
    license="BSD 3-Clause License",
    description="Library for adding Swagger support to clients and servers",
    long_description=open(os.path.join(os.path.dirname(__file__),
                                       "README.rst")).read(),
    author="Digium, Inc. and Yelp, Inc.",
    author_email="opensource+bravado-core@yelp.com",
    url="https://github.com/Yelp/bravado-core",
    packages=["bravado_core"],
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "License :: OSI Approved :: BSD License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 2.6",
        "Programming Language :: Python :: 2.7",
        "Programming Language :: Python :: 3.4",
    ],
    install_requires=[
        "jsonref",
        "jsonschema>=2.5.1",
        "python-dateutil",
        "six",
        "simplejson",
        "swagger-spec-validator>=1.0.12",
    ],
)
