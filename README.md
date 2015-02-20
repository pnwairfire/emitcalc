# emitcalc

This package provides a calculator for computing emissions from
consume output.

## Development

### Install Dependencies

Run the following to install dependencies:

    pip install -r requirements.txt

Run the following for installing development dependencies (like running tests):

    pip install -r dev-requirements.txt

### Setup Environment

To import emitcalc in development, you'll have to add the repo root directory
to the search path.

## Running tests

Use pytest:

    py.test
    py.test test/emitcalc/test_calculator.py

You can also use the ```--collect-only``` option to see a list of all tests.

    py.test --collect-only

See [pytest](http://pytest.org/latest/getting-started.html#getstarted) for more information about

## Installing

The repo is currently public. So, you don't need to be on the FERA bitbucket team
to install from the repo.

### Installing With pip

First, install pip:

    sudo apt-get install python-pip

Then, to install, for example, v0.1.0, use the following:

    sudo pip install git+https://bitbucket.org/fera/airfire-emissions-calculator@v0.1.0

If you get an error like

    AttributeError: 'NoneType' object has no attribute 'skip_requirements_regex

it means you need in upgrade pip.  One way to do so is with the following:

    pip install --upgrade pip

## Usage:

TODO: complete this section
