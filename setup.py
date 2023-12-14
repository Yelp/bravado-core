#!/usr/bin/env python
# -*- coding: utf-8 -*-
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
    long_description=open(
        os.path.join(
            os.path.dirname(__file__),
            "README.rst",
        ),
    ).read(),
    long_description_content_type='text/markdown',
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
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
    install_requires=[
        "jsonref",
        "jsonschema[format-nongpl]>=2.5.1",
        "python-dateutil",
        "pyyaml",
        'requests',
        "simplejson",
        "six",
        "swagger-spec-validator>=2.0.1",
        "pytz",
        "msgpack>=0.5.2",
    ],
    package_data={
        'bravado_core': ['py.typed'],
    },
    python_requires='>=3.7',
)
