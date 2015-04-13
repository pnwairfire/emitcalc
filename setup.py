import re
from setuptools import setup, find_packages

from emitcalc import __version__

test_requirements = []
with open('requirements-test.txt') as f:
    test_requirements = [r for r in f.read().splitlines()]

setup(
    name='emitcalc',
    version=__version__,
    license='MIT',
    author='Joel Dubowy',
    author_email='jdubowy@gmail.com',
    packages=find_packages(),
    scripts=[
        'bin/emitcalc'
    ],
    package_data={
    },
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 2",
        "Operating System :: POSIX",
        "Operating System :: MacOS"
    ],
    url='https://github.com/pnwairfire/emitcalc',
    description='Package providing a calculator for computing emissions from consume output.',
    install_requires=[
        "pyairfire>=0.7.0",
        "eflookup>=0.6.2",
        "numpy==1.8.0"
    ],
    dependency_links=[
        "https://pypi.smoke.airfire.org/simple/pyairfire/",
        "https://pypi.smoke.airfire.org/simple/eflookup/"
    ],
    tests_require=test_requirements
)
