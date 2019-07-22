# -*- coding: utf-8 -*-
 
from setuptools import setup, find_packages
import toughmeshio


DISTNAME = "toughmeshio"
DESCRIPTION = "ToughMeshio"
LONG_DESCRIPTION = "ToughMeshio"
AUTHOR = toughmeshio.__author__
AUTHOR_EMAIL = toughmeshio.__author_email__
URL = toughmeshio.__website__
LICENSE = toughmeshio.__license__
REQUIREMENTS = []
EXTRA_REQUIREMENTS = {
    "all": [
        "meshio",
        "sklearn",
        "numba",
        "joblib",
    ],
    "meshio": [
        "meshio",
    ]
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
        version = toughmeshio.__version__,
        packages = find_packages(),
        include_package_data = True,
    )