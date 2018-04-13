from setuptools import setup, find_packages

from emitcalc import __version__

test_requirements = []
with open('requirements-test.txt') as f:
    test_requirements = [r for r in f.read().splitlines()]

setup(
    name='emitcalc',
    version=__version__,
    license='GPLv3+',
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
        "License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)",
        "Programming Language :: Python :: 2.7",
        "Programming Language :: Python :: 3.5",
        "Operating System :: POSIX",
        "Operating System :: MacOS"
    ],
    url='https://github.com/pnwairfire/emitcalc',
    description='Package providing a calculator for computing emissions from consume output.',
    install_requires=[
        "afscripting>=1.1.2,<2.0.0",
        "eflookup>=v3.1.1,<4.0.0"
        # Note: numpy must now be installed manually beforehand
        # "numpy"
    ],
    dependency_links=[
        "https://pypi.airfire.org/simple/afscripting/"
        "https://pypi.airfire.org/simple/eflookup/"
    ],
    tests_require=test_requirements
)
