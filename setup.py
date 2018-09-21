#!/usr/bin/env python3

"""
Netbox API
"""

from os import path
from setuptools import setup

setup(
    name="netboxapi",
    version="1.1.5",

    description="Client API for Netbox",

    author="Anthony25 <Anthony Ruhier>",
    author_email="anthony.ruhier@gmail.com",

    license="Simplified BSD",

    classifiers=[
        "Programming Language :: Python :: 3 :: Only",
        "License :: OSI Approved :: BSD License",
    ],

    keywords=["netbox", "api"],
    packages=["netboxapi", ],
    install_requires=["requests", ],
    setup_requires=["pytest-runner", ],
    tests_require=[
        "pytest", "pytest-cov", "pytest-mock", "pytest-xdist",
        "requests-mock"
    ],
)
