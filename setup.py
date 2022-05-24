import os
import sys

from setuptools import find_packages, setup

base_dir = os.path.abspath(os.path.dirname(__file__))
about = {}
with open(os.path.join(base_dir, "toughio", "__about__.py"), "rb") as f:
    exec (f.read(), about)


DISTNAME = "toughio"
DESCRIPTION = "Pre- and post-processing Python library for TOUGH"
LONG_DESCRIPTION = open("README.rst").read()
VERSION = about["__version__"]
AUTHOR = about["__author__"]
AUTHOR_EMAIL = about["__author_email__"]
URL = about["__website__"]
LICENSE = about["__license__"]
CLASSIFIERS = [
    "Programming Language :: Python :: 3.6",
    "Programming Language :: Python :: 3.7",
    "Programming Language :: Python :: 3.8",
    "Programming Language :: Python :: 3.9",
    "Development Status :: 5 - Production/Stable",
    "License :: OSI Approved :: BSD License",
    "Natural Language :: English",
    "Operating System :: Microsoft :: Windows",
    "Operating System :: POSIX",
    "Operating System :: MacOS",
    "Intended Audience :: Science/Research",
    "Topic :: Scientific/Engineering",
]

REQUIREMENTS = [
    "meshio >= 4.0.11, < 5.0",
    "numpy >= 1.13.0"
]
EXTRA_REQUIREMENTS = {
    "full": [
        "pyvista >= 0.32, < 0.33",
        "netcdf4",
        "matplotlib",
        "h5py",
        "scipy >= 0.9"
    ],
}


PACKAGE_DATA = {
    "toughio.data": ["CO2TAB"],
}

ENTRY_POINTS = {
    "console_scripts": [
        "toughio-co2tab = toughio._cli:co2tab",
        "toughio-export = toughio._cli:export",
        "toughio-extract = toughio._cli:extract",
        "toughio-merge = toughio._cli:merge",
        "toughio-save2incon = toughio._cli:save2incon",
    ],
}


if __name__ == "__main__":
    setup(
        name=DISTNAME,
        description=DESCRIPTION,
        long_description=LONG_DESCRIPTION,
        long_description_content_type="text/x-rst",
        author=AUTHOR,
        author_email=AUTHOR_EMAIL,
        url=URL,
        license=LICENSE,
        install_requires=REQUIREMENTS,
        extras_require=EXTRA_REQUIREMENTS,
        python_requires="!=3.0.*,!=3.1.*,!=3.2.*,!=3.3.*,!=3.4.*,!=3.5.*",
        classifiers=CLASSIFIERS,
        version=about["__version__"],
        packages=find_packages() + ["toughio.data"],
        package_data=PACKAGE_DATA,
        entry_points=ENTRY_POINTS,
    )
