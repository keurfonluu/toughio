# -*- coding: utf-8 -*-
 
from setuptools import setup, find_packages
import toughio


DISTNAME = "toughio"
DESCRIPTION = "ToughIO"
LONG_DESCRIPTION = "ToughIO"
AUTHOR = toughio.__author__
AUTHOR_EMAIL = toughio.__author_email__
URL = toughio.__website__
LICENSE = toughio.__license__
REQUIREMENTS = []
EXTRA_REQUIREMENTS = {
    ":python_version <= '2.7'": [
        "meshio==2.3.10",
    ],
    ":python_version > '2.7'": [
        "meshio>=3.0.0",
    ],
}
CLASSIFIERS = [
    "Programming Language :: Python",
    "Development Status :: 5 - Production/Stable",
    "License :: OSI Approved :: MIT License",
    "Natural Language :: English",
    "Operating System :: OS Independent",
    "Intended Audience :: Science/Research",
    "Topic :: Scientific/Engineering",
]


if __name__ == "__main__":
    setup(
        name = DISTNAME,
        description = DESCRIPTION,
        long_description = LONG_DESCRIPTION,
        author = AUTHOR,
        author_email = AUTHOR_EMAIL,
        url = URL,
        license = LICENSE,
        install_requires = REQUIREMENTS,
        extras_require = EXTRA_REQUIREMENTS,
        classifiers = CLASSIFIERS,
        version = toughio.__version__,
        packages = find_packages(),
        include_package_data = True,
    )