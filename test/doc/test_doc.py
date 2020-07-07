import os
import subprocess
import sys

import pytest


def test_doc():
    # Path to doc directory
    dirname, _ = os.path.split(os.path.abspath(__file__))
    path_to_doc = dirname.split(os.path.sep)[:-2] + ["doc"]

    # Build doc
    cwd = os.getcwd()

    os.chdir(os.path.sep.join(path_to_doc))
    make = (
        os.path.sep.join(path_to_doc + ["make.bat"])
        if sys.platform == "win32"
        else "make"
    )
    response = subprocess.run([make, "html"])
    assert response.returncode == 0

    os.chdir(cwd)
