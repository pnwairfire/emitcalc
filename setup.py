from distutils.core import setup
from pip.req import parse_requirements

# Note: using pip.req.parse_requirements like so:
#  > REQUIREMENTS = [str(ir.req) for ir in parse_requirements('requirements.txt')]
# results in the folloing error on Heroku:
#    TypeError: parse_requirements() missing 1 required keyword argument: 'session'
with open('requirements.txt') as f:
    REQUIREMENTS = f.read().splitlines()

setup(
    name='emitcalc',
    version='0.1.2',
    author='Joel Dubowy',
    author_email='jdubowy@gmail.com',
    packages=[
        'emitcalc'
    ],
    scripts=[
        'bin/emitcalc'
    ],
    package_data={
    },
    url='https://github.com/pnwairfire/emitcalc',
    description='Package providing a calculator for computing emissions from consume output.',
    install_requires=REQUIREMENTS,
)
