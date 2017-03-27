#!/usr/bin/env python3

"""
Netbox API
"""

from os import path
from setuptools import setup

setup(
    name="netboxapi",
    version="0.0.1",

    description="Client API for Netbox",
    long_description=open(
        path.join(path.dirname(__file__), "README.md")
    ).read(),

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
