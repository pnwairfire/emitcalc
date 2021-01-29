# emitcalc

This package provides a calculator for computing emissions from
consume output.

***This software is provided for research purposes only. It's output may
not accurately reflect observed data due to numerous reasons. Data are
provisional; use at own risk.***

## Python 2 and 3 Support

This package was originally developed to support python 2.7, but has since
been refactored to support 3.5. Attempts to support both 2.7 and 3.5 have
been made but are not guaranteed.

## External Dependencies

You'll need the numpy python package.  This used to be
baked into setup.py, but the version available for install depends
on your platform.

### Mac

    pip install numpy

### Ubuntu (12.04, 14.04, 16.04)

    sudo apt-get install -y python3 python3-dev
    pip install Cython
    pip install numpy

## Development

Via ssh:

    git clone git@github.com:pnwairfire/emitcalc.git

or http:

    git clone https://github.com/pnwairfire/emitcalc.git

### Install python Dependencies

Run the following to install dependencies:

    pip install -r requirements.txt
    pip install -r requirements-test.txt
    pip install -r requirements-dev.txt

#### Notes

##### pip issues

If you get an error like    ```AttributeError: 'NoneType' object has no
attribute 'skip_requirements_regex```, it means you need in upgrade
pip. One way to do so is with the following:

    pip install --upgrade pip

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

### Installing With pip

First, install pip (with sudo if necessary):

    apt-get install python-pip

Then, to install, for example, v2.0.2, use the following (with sudo if necessary):

    pip install --extra-index https://pypi.airfire.org/simple emitcalc==v2.0.2

See the Development > Install Dependencies > Notes section, above, for
notes on resolving pip and gdal issues.

## Usage

### Using emitcalc.calculator.EmissionsCalculator

EmissionsCalculator is passed the output of consume to calculate emissions
along with emission factor lookup objects (one for each set of consumption
values). It produces emissions values for all possible combinations of fuel
category, combustion phase, and chemical species.

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
fuelbeds 1 and 10 (FERA cover types 13 and 130). You could use Fccs2Ef to produce
your two lookup objects:

    >>> from emitcalc.calculator import EmissionsCalculator
    >>> from eflookup.fccs2ef import Fccs2Ef
    >>> fccs2ef = Fccs2Ef(is_rx=True)
    >>> calculator = EmissionsCalculator([fccs2ef['1'],fccs2ef['10']])
    >>> calculator.calculate(consume_output)

or you could use CoverType2Ef:

    >>> from emitcalc.calculator import EmissionsCalculator
    >>> from eflookup.fccs2ef import CoverType2Ef
    >>> ct2ef = CoverType2Ef(is_rx=True)
    >>> calculator = EmissionsCalculator([ct2ef['13'], ct2ef['130']])
    >>> calculator.calculate(consume_output)

or you could use FEPS model, fuelbed agnostic EFs:

    >>> from emitcalc.calculator import EmissionsCalculator
    >>> from eflookup.fepsef import FepsEFLookup
    >>> fepsef = FepsEFLookup()
    >>> calculator = EmissionsCalculator(fepsef)
    >>> calculator.calculate(consume_output)

or you could use a custom EF look-up object, which can be built using
[eflookup's](https://github.com/pnwairfire/eflookup) BasicEFLookup class.

    >>> from eflookup.lookup import BasicEFLookup
    >>> from emitcalc.calculator import EmissionsCalculator
    >>> EFS = {
        'flaming': {
            'CO': 0.07179999999999997,
        },
        'residual': {
            'PM10': 0.01962576,
        },
        'smoldering': {
            'NH3': 0.00341056,
        }
    }
    >>> look_up = BasicEFLookup(EFS)
    >>> calculator = EmissionsCalculator(look_up)
    >>> calculator.calculate(consume_output)

Note that any emission factor lookup class that supports the following
interface can be used:

    get(phase=PHASE, fuel_category=FUEL_CATEGORY, species=SPECIES)
    species(phase) # returns all chemical species produced by the phase

Also note that, in the FepsEFLookup and BasicEFLookup examples, the calculator was
instantiated with a single lookup object instead of an array of fuelbed-specific
lookup objects. This is valid in the case where emission factors don't vary from
fuelbed to fuelbed,

The emissions calculator will produce values for whatever chemical species are
represented in the lookup object.  So, for example, using ```look_up```, you'd
get the following limited set of emissions:

    {
        'ground fuels': {
            'basal accumulations': {
                'flaming': {
                    'CO': [3.3815120047017005e-05,
                        0.012923999999999995
                    ]
                },
                'residual': {
                    'PM10': [4.621500211796271e-05, 0.0003925152]
                },
                'smoldering': {
                    'NH3': [6.424985839975172e-06, 0.0007844288]
                }
            },
            'duff lower': {
                'flaming': {
                    'CO': [0.0, 0.0]
                },
                'residual': {
                    'PM10': [0.0, 0.0]
                },
                'smoldering': {
                    'NH3': [0.0, 0.0]
                }
            }
        },
        'litter-lichen-moss': {
            'lichen': {
                'flaming': {
                    'CO': [0.0, 0.0]
                },
                'residual': {
                    'PM10': [0.0, 0.0]
                },
                'smoldering': {
                    'NH3': [0.0, 0.0]
                }
            },
            'litter': {
                'flaming': {
                    'CO': [0.17116545599999997, 0.07897999999999998]
                },
                'residual': {
                    'PM10': [0.0, 0.0]
                },
                'smoldering': {
                    'NH3': [0.0009033891328, 0.00341056]
                }
            }
        },
        'summary': {
            'ground fuels': {
                'flaming': {
                    'CO': [3.3815120047017005e-05,
                        0.012923999999999995
                    ]
                },
                'residual': {
                    'PM10': [4.621500211796271e-05, 0.0003925152]
                },
                'smoldering': {
                    'NH3': [6.424985839975172e-06, 0.0007844288]
                }
            },
            'litter-lichen-moss': {
                'flaming': {
                    'CO': [0.17116545599999997,
                        0.07897999999999998
                    ]
                },
                'residual': {
                    'PM10': [0.0, 0.0]
                },
                'smoldering': {
                    'NH3': [0.0009033891328, 0.00341056]
                }
            },
            'total': {
                'flaming': {
                    'CO': [0.1795595846677937, 0.09980199999999997]
                },
                'residual': {
                    'PM10': [0.005759220127912722, 0.006672758399999999]
                },
                'smoldering': {
                    'NH3': [0.0015054969384185898, 0.004604256]
                },
                'total': {
                    'CO': [0.1795595846677937, 0.09980199999999997],
                    'NH3': [0.0015054969384185898, 0.004604256],
                    'PM10': [0.005759220127912722, 0.006672758399999999]
                }
            },
            'woody fuels': {
                'flaming': {
                    'CO': [0.008360313547746709,
                        0.007897999999999997
                    ]
                },
                'residual': {
                    'PM10': [0.005713005125794759, 0.0062802432]
                },
                'smoldering': {
                    'NH3': [0.0005956828197786147, 0.00040926719999999996]
                }
            }
        },
        'woody fuels': {
            '1000-hr fuels rotten': {
                'flaming': {
                    'CO': [0.008360313547746709,
                        0.007897999999999997
                    ]
                },
                'residual': {
                    'PM10': [0.005713005125794759, 0.0062802432]
                },
                'smoldering': {
                    'NH3': [0.0005956828197786147, 0.00040926719999999996]
                }
            },
            'stumps rotten': {
                'flaming': {
                    'CO': [0.0, 0.0]
                },
                'residual': {
                    'PM10': [0.0, 0.0]
                },
                'smoldering': {
                    'NH3': [0.0, 0.0]
                }
            }
        }
    }

If the lookup object has different EF sets for each fuelbed, the arrays of
emissions values will be filled in with ```0.0``` appropriately.  The
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
        "ground fuels": {
            "basal accumulations": {
                "smoldering": [0.14949327591400063, 0.2],
                "total": [1.4949327591400063, 1.34],
                "flaming": [1.3454394832260057, 1.14],
                "residual": [1.12, 0.32]
            }
        },
        "summary": {
            "litter-lichen-moss": {
                "smoldering": [0.14949327591400063, 0.2],
                "total": [1.4949327591400063, 1.34],
                "flaming": [1.3454394832260057, 1.14],
                "residual": [0.0, 0.0]
            },
            "ground fuels": {
                "smoldering": [0.14949327591400063, 0.2],
                "total": [1.4949327591400063, 1.34],
                "flaming": [1.3454394832260057, 1.14],
                "residual": [1.12, 0.32]
            }
        }
    }
    >>> from emitcalc.calculator import EmissionsCalculator
    >>> from eflookup.lookup import BasicEFLookup
    >>> EFS_A = {
        'flaming': {'CO': 14.0,'PM10': 15.2},
        'smoldering': {'CO2': 140.23,'PM2.5': 15.2},
        'residual': {'CO': 140.0,'NM': 23.0}
    }
    >>> EFS_B = {
        'flaming': {'CO2': 123.23},
        'smoldering': {'CO': 10.0},
        'residual': {'CO2': 3.23,'FDF': 2.32}
    }
    >>> calculator = EmissionsCalculator([BasicEFLookup(EFS_A), BasicEFLookup(EFS_B)])
    >>> calculator.calculate(consume_output)

    {
        'ground fuels': {
            'basal accumulations': {
                'flaming': {
                    'CO': [18.83615276516408,
                        0.0
                    ],
                    'CO2': [0.0, 140.4822],
                    'PM10': [20.450680145035285, 0.0]
                },
                'residual': {
                    'CO': [156.8, 0.0],
                    'CO2': [0.0, 1.0336],
                    'FDF': [0.0, 0.7424],
                    'NM': [25.76, 0.0]
                },
                'smoldering': {
                    'CO': [0.0, 2.0],
                    'CO2': [20.963442081420308, 0.0],
                    'PM2.5': [2.2722977938928097, 0.0]
                }
            }
        },
        'litter-lichen-moss': {
            'litter': {
                'flaming': {
                    'CO': [18.83615276516408, 0.0],
                    'CO2': [0.0, 17.252200000000002],
                    'PM10': [20.450680145035285, 0.0]
                },
                'residual': {
                    'CO': [0.0, 0.0],
                    'CO2': [0.0, 0.0],
                    'FDF': [0.0, 0.0],
                    'NM': [0.0, 0.0]
                },
                'smoldering': {
                    'CO': [0.0, 2.0],
                    'CO2': [20.963442081420308, 0.0],
                    'PM2.5': [2.2722977938928097, 0.0]
                }
            }
        },
        'summary': {
            'ground fuels': {
                'flaming': {
                    'CO': [18.83615276516408, 0.0],
                    'CO2': [0.0, 140.4822],
                    'PM10': [20.450680145035285, 0.0]
                },
                'residual': {
                    'CO': [156.8, 0.0],
                    'CO2': [0.0, 1.0336],
                    'FDF': [0.0, 0.7424],
                    'NM': [25.76, 0.0]
                },
                'smoldering': {
                    'CO': [0.0, 2.0],
                    'CO2': [20.963442081420308, 0.0],
                    'PM2.5': [2.2722977938928097, 0.0]
                }
            },
            'litter-lichen-moss': {
                'flaming': {
                    'CO': [18.83615276516408, 0.0],
                    'CO2': [0.0, 17.252200000000002],
                    'PM10': [20.450680145035285, 0.0]
                },
                'residual': {
                    'CO': [0.0, 0.0],
                    'CO2': [0.0, 0.0],
                    'FDF': [0.0, 0.0],
                    'NM': [0.0, 0.0]
                },
                'smoldering': {
                    'CO': [0.0, 2.0],
                    'CO2': [20.963442081420308, 0.0],
                    'PM2.5': [2.2722977938928097, 0.0]
                }
            },
            'total': {
                'flaming': {
                    'CO': [37.67230553032816, 0.0],
                    'CO2': [0.0, 157.7344],
                    'PM10': [40.90136029007057, 0.0]
                },
                'residual': {
                    'CO': [156.8, 0.0],
                    'CO2': [0.0, 1.0336],
                    'FDF': [0.0, 0.7424],
                    'NM': [25.76, 0.0]
                },
                'smoldering': {
                    'CO': [0.0, 4.0],
                    'CO2': [41.926884162840615, 0.0],
                    'PM2.5': [4.5445955877856195, 0.0]
                },
                'total': {
                    'CO': [194.47230553032819, 4.0],
                    'CO2': [41.926884162840615, 158.768],
                    'FDF': [0.0, 0.7424],
                    'NM': [25.76, 0.0],
                    'PM10': [40.90136029007057, 0.0],
                    'PM2.5': [4.5445955877856195, 0.0]
                }
            }
        }
    }

Note from the above examples that the emissions calculator produces
a 'summary' section.  The values in this section are computed from the
individual emissions for the fuel categories, not from the 'summary'
section in the consume output.  If the consume output has a 'summary'
section, it is ignored.

#### Invalid / Missing Data

EmissionsCalculator iterates through the consume output, computing
emissions for each of the nested dictionaries in that output (with
the exception of 'summary' or 'debug' dictionaries, which it ignores).
How it handles invalid or missing data depends on what's missing
or how the data are invalid.

##### Missing Combustion Phase

In the event where the consume output is missing data for a combustion
phase, such as in the following example, which lacks 'flaming'
consumption for the 'litter' fuel category,

    {
        ...,
        "litter-lichen-moss": {
            "litter": { # <-- Missing 'flaming'
                "smoldering": [0.149, 0.2],
                "residual": [0.0, 0.0],
                "total": [1.4949, 0.34]
            },
            ...
         }
    }

the emissions calculator assumes there was no flaming consumption
and sets the flaming emissions to zero values.

##### Missing or Extra Values In Consumption Data Array

When any of the arrays of consumption data have length not equal to
the number of fuelbed ids, such as in the following example (assuming
two fuel bed ids):

     {
        ...,
        "litter-lichen-moss": {
            "litter": {
                "flaming [0.149],  # <-- only has one value
                "smoldering": [0.149, 0.2],
                "total": [1.4949, 0.34],
                "residual": [0.0, 0.0]
            },
            ...
         }
    }

the emissions calculator raises a ```ValueError``` exception, unless
it was constructed in 'silent_fail' mode (see below).

#### ```silent_fail``` Mode

When run in this mode, the emissions calculator will simply ignore
and skip any invalid consumption data that it encounters, rather
than raise an exception.  The calculator is instantiated in
```silent_fail``` like this:

    >>> ...
    >>> calculator = EmissionsCalculator(look_up, silent_fail=True)

#### Species Whitelist

You can specify a subset of chemical species for which the calulator should
compute emissions by instantiating the calculator with the ```species```
option.  For example, to only compute CO2 and PM2.5 levels:

    >>> ...
    >>> calculator = EmissionsCalculator(look_up, species=['CO2', 'PM2.5'])
