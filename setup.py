#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright (c) 2013, Digium, Inc.
# Copyright (c) 2014-2015, Yelp, Inc.
import os
import sys

from setuptools import setup

import bravado_core

install_requires = [
    "jsonref",
    "jsonschema[format]>=2.5.1",
    "python-dateutil",
    "pyyaml",
    'requests',
    "simplejson",
    "six",
    "swagger-spec-validator>=2.0.1",
    "pytz",
    "msgpack>=0.5.2",
]

# pyrsistent dropped python2 support in 0.17.0
if sys.version_info < (3, 5):
    install_requires.append('pyrsistent<0.17')

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
        "Programming Language :: Python :: 2.7",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
    ],
    install_requires=install_requires,
    package_data={
        'bravado_core': ['py.typed'],
    },
    # https://mypy.readthedocs.io/en/latest/installed_packages.html
    zip_safe=False,
    extras_require={
        ':python_version<"3.5"': ['typing'],
        ':python_version<"3.4"': ['enum34'],
        ':python_version<"3.2"': ['functools32'],
    },
    python_requires='!=3.0,!=3.1,!=3.2,!=3.3,!=3.4,!=3.5.0',
)
