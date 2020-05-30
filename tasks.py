import shutil
from invoke import task

import toughio


@task
def build(c):
    shutil.rmtree("dist", ignore_errors=True)
    c.run("python setup.py sdist bdist_wheel")


@task
def tag(c):
    c.run("git tag v{}".format(toughio.__version__))
    c.run("git push --tags")


@task
def upload(c):
    c.run("twine upload dist/*")


@task
def clean(c):
    patterns = [
        "build",
        "dist",
        "toughio.egg-info",
    ]
    for pattern in patterns:
        shutil.rmtree(pattern, ignore_errors=True)


@task
def black(c):
    c.run("black -t py27 toughio")
    c.run("black -t py27 test")


@task
def docstring(c):
    c.run("docformatter -r -i --blank --wrap-summaries 88 --wrap-descriptions 88 --pre-summary-newline toughio")


@task
def isort(c):
    c.run("isort -rc toughio")
    c.run("isort -rc test")


@task
def format(c):
    c.run("invoke isort black docstring")
