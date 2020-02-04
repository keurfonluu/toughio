import os

from setuptools import find_packages, setup

base_dir = os.path.abspath(os.path.dirname(__file__))
about = {}
with open(os.path.join(base_dir, "toughio", "__about__.py"), "rb") as f:
    exec(f.read(), about)


DISTNAME = "toughio"
DESCRIPTION = "toughio"
LONG_DESCRIPTION = "toughio"
VERSION = about["__version__"]
AUTHOR = about["__author__"]
AUTHOR_EMAIL = about["__author_email__"]
URL = about["__website__"]
LICENSE = about["__license__"]
REQUIREMENTS = [
    "meshio == 2.3.10; python_version <= '2.7'",
    "meshio >= 3.0.0; python_version > '2.7'",
]
EXTRA_REQUIREMENTS = {
    "full": [
        "pyvista == 0.22.4; python_version <= '2.7'",
        "pyvista >= 0.23.1; python_version > '2.7'",
    ],
}
CLASSIFIERS = [
    "Programming Language :: Python :: 2.7",
    "Programming Language :: Python :: 3.5",
    "Programming Language :: Python :: 3.6",
    "Programming Language :: Python :: 3.7",
    "Programming Language :: Python :: 3.8",
    "Development Status :: 5 - Production/Stable",
    "License :: OSI Approved :: MIT License",
    "Natural Language :: English",
    "Operating System :: Microsoft :: Windows",
    "Operating System :: POSIX",
    "Operating System :: MacOS",
    "Intended Audience :: Science/Research",
    "Topic :: Scientific/Engineering",
]


if __name__ == "__main__":
    setup(
        name=DISTNAME,
        description=DESCRIPTION,
        long_description=LONG_DESCRIPTION,
        author=AUTHOR,
        author_email=AUTHOR_EMAIL,
        url=URL,
        license=LICENSE,
        install_requires=REQUIREMENTS,
        extras_require=EXTRA_REQUIREMENTS,
        classifiers=CLASSIFIERS,
        version=about["__version__"],
        packages=find_packages(),
        include_package_data=True,
    )
