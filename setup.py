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
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "License :: OSI Approved :: BSD License",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
    ],
    install_requires=[
        "jsonref",
        "jsonschema",
        "python-dateutil",
        "simplejson",
        "swagger-spec-validator",
    ],
)
