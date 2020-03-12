import os
import sys

from setuptools import find_packages, setup

base_dir = os.path.abspath(os.path.dirname(__file__))
about = {}
with open(os.path.join(base_dir, "toughio", "__about__.py"), "rb") as f:
    exec (f.read(), about)


DISTNAME = "toughio"
DESCRIPTION = "Pre- and post-processing Python library for TOUGH"
LONG_DESCRIPTION = open("README.md").read()
VERSION = about["__version__"]
AUTHOR = about["__author__"]
AUTHOR_EMAIL = about["__author_email__"]
URL = about["__website__"]
LICENSE = about["__license__"]
CLASSIFIERS = [
    "Programming Language :: Python :: 2.7",
    "Programming Language :: Python :: 3.5",
    "Programming Language :: Python :: 3.6",
    "Programming Language :: Python :: 3.7",
    "Development Status :: 5 - Production/Stable",
    "License :: OSI Approved :: MIT License",
    "Natural Language :: English",
    "Operating System :: Microsoft :: Windows",
    "Operating System :: POSIX",
    "Operating System :: MacOS",
    "Intended Audience :: Science/Research",
    "Topic :: Scientific/Engineering",
]

# TODO: use new environment markers when dropping support for python < 3
# REQUIREMENTS = [
#     "meshio == 2.3.10; python_version <= '2.7'",
#     "meshio >= 3.0.0; python_version > '2.7'",
# ]
# EXTRA_REQUIREMENTS = {
#     "full": [
#         "pyvista == 0.22.4; python_version <= '2.7'",
#         "pyvista >= 0.23.1; python_version > '2.7'",
#     ],
# }
if sys.version_info < (3,):
    REQUIREMENTS = ["meshio == 2.3.10"]
    EXTRA_REQUIREMENTS = {"full": ["pyvista == 0.22.4"]}
else:
    REQUIREMENTS = ["meshio >= 4.0.7, < 5.0"]
    EXTRA_REQUIREMENTS = {"full": ["pyvista >= 0.23.1"]}
REQUIREMENTS += ["numpy >= 1.13.0"]
EXTRA_REQUIREMENTS["full"] += ["netcdf4", "h5py", "scipy>=0.9"]

ENTRY_POINTS = {
    "console_scripts": [
        "toughio-export = toughio._cli:export",
        "toughio-extract = toughio._cli:extract",
        "toughio-merge = toughio._cli:merge",
    ],
}


if __name__ == "__main__":
    setup(
        name=DISTNAME,
        description=DESCRIPTION,
        long_description=LONG_DESCRIPTION,
        long_description_content_type="text/markdown",
        author=AUTHOR,
        author_email=AUTHOR_EMAIL,
        url=URL,
        license=LICENSE,
        install_requires=REQUIREMENTS,
        extras_require=EXTRA_REQUIREMENTS,
        python_requires=">=2.7,!=3.0.*,!=3.1.*,!=3.2.*,!=3.3.*,!=3.4.*",
        classifiers=CLASSIFIERS,
        version=about["__version__"],
        packages=find_packages(),
        include_package_data=True,
        entry_points=ENTRY_POINTS,
    )
