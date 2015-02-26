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

For example, assume you have the following (pruned) output from consume:

    >>> consume_output = {
            "litter-lichen-moss": {
                "litter": {
                    "smoldering": [0.26488, 1],
                    "total": [2.6488, 2.1],
                    "flaming": [2.3839200000000003, 1.1],
                    "residual": [0.0, 0.0]
                },
                "lichen": {
                    "smoldering": [0.0, 0.0],
                    "total": [0.0, 0.0],
                    "flaming": [0.0, 0.0],
                    "residual": [0.0, 0.0]
                }
                # ... other sub-categories would be here
            },
            "ground fuels": {
                "duff lower": {
                    "smoldering": [0.0, 0.0],
                    "total": [0.0, 0.0],
                    "flaming": [0.0, 0.0],
                    "residual": [0.0, 0.0]
                },
                "basal accumulations": {
                    "smoldering": [0.0018838506989981624, 0.23],
                    "total": [0.004709626747495406, 0.43],
                    "flaming": [0.0004709626747495406, 0.18],
                    "residual": [0.002354813373747703, 0.02]
                }
                # ... other sub-categories would be here
            },
            "woody fuels": {
                "1000-hr fuels rotten": {
                    "smoldering": [0.17465836102534912, 0.12],
                    "total": [0.5821945367511637, 0.55],
                    "flaming": [0.11643890735023275, 0.11],
                    "residual": [0.29109726837558186, 0.32]
                },
                "stumps rotten": {
                    "smoldering": [0.0, 0.0],
                    "total": [0.0, 0.0],
                    "flaming": [0.0, 0.0],
                    "residual": [0.0, 0.0]
                }
                # ... other sub-categories would be here
            },
            # ... other categories would be here ...
            "summary": {
                "litter-lichen-moss": {
                    "smoldering": [0.26488, 0.2],
                    "total": [2.6488, 1.1],
                    "flaming": [2.3839200000000003, 0.9],
                    "residual": [0.0, 0.0]
                },
                # ... other categories would be here
                "total": {
                    "smoldering": [2.411645203171406, 1.2],
                    "total": [10.843917000136159, 9.2],
                    "flaming": [6.9149277822157575, 0.5],
                    "residual": [1.5173440147489938, 7.5]
                }
            }
        }

Now, let's say the consumption was for an Rx burn on land representing FCCS
fuelbeds 1 and 10 (FERA cover types 13 and 130). You could use an instance of
Fccs2Ef as your lookup object:

    >>> from emitcalc.calculator import EmissionsCalculator
    >>> from fccs2ef.lookup import Fccs2Ef
    >>> calculator = EmissionsCalculator(Fccs2Ef())
    >>> calculator.calculate(['1','10'], consume_output, True)

or you could use CoverType2Ef:

    >>> from emitcalc.calculator import EmissionsCalculator
    >>> from fccs2ef.lookup import CoverType2Ef
    >>> calculator = EmissionsCalculator(CoverType2Ef())
    >>> calculator.calculate(['13', '130'], consume_output, True)

or you could use a dict (in this case, using with cover type ids as the keys):

    >>> from emitcalc.calculator import EmissionsCalculator
    >>> look_up = {
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
    >>> calculator = EmissionsCalculator(look_up)
    >>> calculator.calculate(['13','130'], consume_output, True)

The emissions calculator will produce values for whatever chemical species are
represented in the lookup object.  So, for example, using ```look_up```, you'd
get the following limited set of emissions:

    {
        'ground fuels': {
            'basal accumulations': {
                'flaming': {
                    'C02': [0.06604309588012808, 21.6414],
                    'CO': [0.006122514771744028, 1.7999999999999998]
                },
                'residual': {
                    'C02': [0.010714400850552048, 0.0646],
                    'CO': [0.3296738723246784, 2.4]
                },
                'smoldering': {
                    'C02': [0.2641723835205123, 27.652900000000002],
                    'CO': [0.024490059086976112, 2.3000000000000003]
                }
            },
            'duff lower': {
                'flaming': {
                    'C02': [0.0, 0.0],
                    'CO': [0.0, 0.0]
                },
                'residual': {
                    'C02': [0.0, 0.0],
                    'CO': [0.0, 0.0]
                },
                'smoldering': {
                    'C02': [0.0, 0.0],
                    'CO': [0.0, 0.0]
                }
            }
        },
        'litter-lichen-moss': {
            'lichen': {
                'flaming': {
                    'C02': [0.0, 0.0],
                    'CO': [0.0, 0.0]
                },
                'smoldering': {
                    'C02': [0.0, 0.0],
                    'CO': [0.0, 0.0]
                }
            },
            'litter': {
                'flaming': {
                    'C02': [334.2971016, 132.25300000000001],
                    'CO': [30.990960000000005, 11.0]
                },
                'smoldering': {
                    'C02': [37.1441224, 120.23],
                    'CO': [3.44344, 10.0]
                }
            }
        },
        'summary': {
            'litter-lichen-moss': {
                'flaming': {
                    'C02': [334.2971016, 108.20700000000001],
                    'CO': [30.990960000000005, 9.0]
                },
                'smoldering': {
                    'C02': [37.1441224, 24.046000000000003],
                    'CO': [3.44344, 2.0]
                }
            },
            'total': {
                'flaming': {
                    'C02': [969.6803229001156, 60.115],
                    'CO': [89.89406116880485, 5.0]
                },
                'smoldering': {
                    'C02': [338.18500684072626, 144.276],
                    'CO': [31.35138764122828, 12.0]
                }
            }
        },
        'woody fuels': {
            '1000-hr fuels rotten': {
                'flaming': {
                    'C02': [16.328227977723138, 13.2253],
                    'CO': [1.5137057955530258, 1.1]
                },
                'residual': {
                    'C02': [1.2924718715875836, 1.0336],
                    'CO': [40.75361757258146, 38.4]
                },
                'smoldering': {
                    'C02': [24.492341966584707, 14.4276],
                    'CO': [2.2705586933295385, 1.2]
                }
            },
            'stumps rotten': {
                'flaming': {
                    'C02': [0.0, 0.0],
                    'CO': [0.0, 0.0]
                },
                'residual': {
                    'C02': [0.0, 0.0],
                    'CO': [0.0, 0.0]
                },
                'smoldering': {
                    'C02': [0.0, 0.0],
                    'CO': [0.0, 0.0]
                }
            }
        }
    }

If the lookup object has different EF sets for each fuelbed, the arrays of
emissions values will be filled in with ```None``` appropriately.  The
following example illustrates this:


    >>> consume_output = {
            "litter-lichen-moss": {
                "litter": {
                    "smoldering": [0.14949327591400063, 0.2],
                    "total": [1.4949327591400063, 0.34],
                    "flaming": [1.3454394832260057, 0.14],
                    "residual": [0.0, 0.0]
                }
            },
            "summary": {
                "litter-lichen-moss": {
                    "smoldering": [0.14949327591400063, 0.2],
                    "total": [1.4949327591400063, 1.34],
                    "flaming": [1.3454394832260057, 1.14],
                    "residual": [0.0, 0.0]
                }
            }
        }
    >>> from emitcalc.calculator import EmissionsCalculator
    >>> look_up = {
            '13': {
                'flame_smold_wf': {
                    'CO': 14.0,
                    'PM2.5': 15.2
                },
                'flame_smold_rx': {
                    'C02': 140.23
                },
                'woody_rsc': {
                    'CO': 140.0,
                    'NM': 23.0
                },
                'duff_rsc': {
                    'C02': 4.55
                }
            },
            '130': {
                'flame_smold_wf': {
                    'C02': 123.23
                },
                'flame_smold_rx': {
                    'CO': 10.0
                },
                'woody_rsc': {
                    'C02': 3.23,
                    'FDF': 2.32
                },
                'duff_rsc': {
                    'CO': 120.0
                }
            }
        }
    >>> calculator = EmissionsCalculator(look_up)
    >>> calculator.calculate(['13','130'], consume_output, True)

    TODO: FILL THIS IN
