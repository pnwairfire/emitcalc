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

## Usage

### Using emitcalc.calculator.EmissionsCalculator

EmissionsCalculator is constructed with an emissions factor lookup object
(or dictionary), and then passed the output of consume to calculate emissions.
It produces emissions values for all possible combinations of fuel category,
combustion phase, and chemical species.

For example, assume you have the following output from consume:

    consume_output = {
        "litter-lichen-moss": {
            "litter": {
                "smoldering": [0.14949327591400063, 0.2],
                "total": [1.4949327591400063, 0.34],
                "flaming": [1.3454394832260057, 0.14],
                "residual": [0.0, 0.0]
            },
            "lichen": {
                "smoldering": [0.0, 0.0],
                "total": [0.0, 0.0],
                "flaming": [0.0, 0.0],
                "residual": [0.0, 0.0]
            },
            "moss": {
                "smoldering": [0.0, 0.0],
                "total": [0.0, 0.0],
                "flaming": [0.0, 0.0],
                "residual": [0.0, 0.0]
            }
        },
        # ... other categories would be here ...
        "summary": {
            "litter-lichen-moss": {
                "smoldering": [0.14949327591400063, 1.3],
                "total": [1.4949327591400063, 1.3],
                "flaming": [1.3454394832260057, 1.2],
                "residual": [0.0, 0.0]
            },
            # ... other categories would be here
            "total": {
                "smoldering": [0.5204272058409944, 0.4],
                "total": [8.12290643708535, 8.1],
                "flaming": [7.582869231244354, 7.2],
                "residual": [0.019610000000000002, 0.013]
            }
        }
    }

Now, let's say the consumption was for an Rx burn on land representing FCCS
fuelbeds 1 and 10 (FERA cover types 13 and 130). You could use an instance of
Fccs2Ef as your lookup object:

    from emitcalc.calculator import EmissionsCalculator
    from fccs2ef.lookup import Fccs2Ef
    calculator = EmissionsCalculator(Fccs2Ef())
    calculator.calculate(['1','10'], consume_output, True)

or you could use CoverType2Ef:

    from emitcalc.calculator import EmissionsCalculator
    from fccs2ef.lookup import CoverType2Ef
    calculator = EmissionsCalculator(CoverType2Ef())
    calculator.calculate(['13', '130'], consume_output, True)

or you could use a dict (in this case, using with cover type ids as the keys):

    from emitcalc.calculator import EmissionsCalculator
    look_up = {
        '13': {
            'flame_smold_wf': {
                'C02': 143.23,
                'CO': 14.0
            },
            'flame_smold_rx': {
                'C02': 140.23,
                'CO': 13.0
            },
            'woody_rsc': {
                'C02': 4.44,
                'CO': 140.0
            },
            'duff_rsc': {
                'C02': 4.55,
                'CO': 140.0
            }
        },
        '130': {
            'flame_smold_wf': {
                'C02': 123.23,
                'CO': 12.0
            },
            'flame_smold_rx': {
                'C02': 120.23,
                'CO': 10.0
            },
            'woody_rsc': {
                'C02': 3.23,
                'CO': 120.0
            },
            'duff_rsc': {
                'C02': 3.23,
                'CO': 120.0
            }
        }
    }
    calculator = EmissionsCalculator(look_up)
    calculator.calculate(['13','130'], consume_output, True)

The emissions calculator will produce values for whatever chemical species are
represented in the lookup object.  So, for example, using ```look_up```, you'd
get the following limited set of emissions:


# TODO: UPDATE THE FOLLOWING OUTPUT...IT SHOULD CONTAIN ARRAYS OF VALUES...

    {
        'litter-lichen-moss': {
            'lichen': {
                'flaming': {
                    'C02': 0.0,
                    'CO': 0.0
                },
                'smoldering': {
                    'C02': 0.0,
                    'CO': 0.0
                }
            },
            'litter': {
                'flaming': {
                    'C02': 161.76218906826267,
                    'CO': 13.454394832260057
                },
                'smoldering': {
                    'C02': 17.9735765631403,
                    'CO': 1.4949327591400063
                }
            },
            'moss': {
                'flaming': {'C02': 0.0, 'CO': 0.0},
                'smoldering': {'C02': 0.0, 'CO': 0.0}
            }
        },
        # ... other categories would be here ...
        'summary': {
            'litter-lichen-moss': {
                'flaming': {
                    'C02': 161.76218906826267,
                    'CO': 13.454394832260057},
                'smoldering': {
                    'C02': 17.9735765631403,
                    'CO': 1.4949327591400063
                }
            },
            # ... other categories would be here ...
            'total': {
                'flaming': {
                    'C02': 911.6883676725087,
                    'CO': 75.82869231244354
                },
               'smoldering': {
                    'C02': 62.57096295826276,
                    'CO': 5.204272058409945
                }
            }
        }
    }

