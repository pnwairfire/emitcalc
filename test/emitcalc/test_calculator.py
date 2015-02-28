__author__      = "Joel Dubowy"
__copyright__   = "Copyright 2014, AirFire, PNW, USFS"

from numpy.testing import assert_approx_equal
from py.test import raises#, mark

from emitcalc.calculator import EmissionsCalculator

LOOK_UP = {
    '13': {
        'flame_smold_wf': {'CO2': 143.23,'CO': 14.0},
        'flame_smold_rx': {'CO2': 140.23,'CO': 13.0},
        'woody_rsc': {'CO2': 4.44,'CO': 140.0},
        'duff_rsc': {'CO2': 4.55,'CO': 140.0}
    },
    '130': {
        'flame_smold_wf': {'CO2': 123.23,'CO': 12.0},
        'flame_smold_rx': {'CO2': 120.23,'CO': 10.0},
        'woody_rsc': {'CO2': 3.23,'CO': 120.0},
        'duff_rsc': {'CO2': 3.23,'CO': 120.0}
    }
}
LOOK_UP_DIFFERING = {
    '13': {
        'flame_smold_wf': {'CO': 14.0,'PM10': 15.2},
        'flame_smold_rx': {'CO2': 140.23,'PM2.5': 15.2},
        'woody_rsc': {'CO': 140.0,'NM': 23.0},
        'duff_rsc': {'CO2': 4.55}
    },
    '130': {
        'flame_smold_wf': {'CO2': 123.23},
        'flame_smold_rx': {'CO': 10.0},
        'woody_rsc': {'CO2': 3.23,'FDF': 2.32},
        'duff_rsc': {'CO': 120.0}
    }
}

def assert_results_are_approximately_equal(expected, actual):
    # categories
    assert set(expected.keys()) == set(actual.keys())
    for c in expected.keys():
        print '- %s' % (c)
        # sub-categories
        assert set(expected[c].keys()) == set(actual[c].keys())
        for sc in expected[c].keys():
            print ' - %s' % (sc)
            # combustion phases
            assert set(expected[c][sc].keys()) == set(actual[c][sc].keys())
            for cp in expected[c][sc].keys():
                print '  - %s' % (cp)
                # chemical species
                assert set(expected[c][sc][cp].keys()) == set(actual[c][sc][cp].keys())
                for s in expected[c][sc][cp].keys():
                    print '   - %s' % (s)
                    # emissions values
                    assert len(expected[c][sc][cp][s]) == len(actual[c][sc][cp][s])
                    for i in xrange(len(expected[c][sc][cp][s])):
                        assert_approx_equal(
                            expected[c][sc][cp][s][i],
                            actual[c][sc][cp][s][i],
                            significant=8  # arbitrarily chose 8
                        )



class TestEmissionsCalculator:

    def test_missing_efs(self):
        consume_output = {
            "litter-lichen-moss": {
                "litter": { # <-- Missing 'flaming'
                    "smoldering": [0.14949327591400063, 0.2],
                    "total": [1.4949327591400063, 0.34],
                    "residual": [0.0, 0.0]
                }
            }
        }
        with raises(KeyError) as e:
            # No EFs for '13sdf'
            EmissionsCalculator(LOOK_UP).calculate(['13sdf','130'],
                consume_output, True)

    def test_missing_combustion_phase_keys(self):
        consume_output = {
            "litter-lichen-moss": {
                "litter": { # <-- Missing 'flaming'
                    "smoldering": [0.14949327591400063, 0.2],
                    "total": [1.4949327591400063, 0.34],
                    "residual": [0.0, 0.0]
                }
            },
            "ground fuels": {
                "basal accumulations": {
                    "smoldering": [0.14949327591400063, 0.2],
                    "total": [1.4949327591400063, 1.34],
                    "flaming": [1.3454394832260057, 1.14],
                    "residual": [2.0, 0.3]
                },
                "blah": { # <-- Missing 'flaming' and 'smoldering'
                    "residual": [0.0, 0.0]
                }
            }
        }
        with raises(ValueError) as e:
             EmissionsCalculator(LOOK_UP).calculate(['13','130'],
                consume_output, True)
        calculator = EmissionsCalculator(LOOK_UP, silent_fail=True)
        emissions = calculator.calculate(['13','130'], consume_output, True)
        assert 0 == len(emissions["litter-lichen-moss"].keys())  # <-- "litter" should have been skipped
        assert 1 == len(emissions["ground fuels"].keys())  # <-- "blah" should have been skipped
        expected = {
            "litter-lichen-moss": {},
            'ground fuels': {
                'basal accumulations': {
                    'flaming': {
                        'CO2': [188.67097873278277, 137.0622],
                        'CO': [17.490713281938074, 11.399999999999999]
                    },
                    'smoldering': {
                        'CO2': [20.963442081420308, 24.046000000000003],
                        'CO': [1.9434125868820082, 2.0]
                    },
                    'residual': {
                        'CO2': [9.1, 0.969],
                        'CO': [280.0, 36.0]
                    }
                }
            }
        }
        assert_results_are_approximately_equal(expected, emissions)

    def test_differing_number_of_consumption_values(self):
        consume_output = {
            "litter-lichen-moss": {
                "litter": {
                    "smoldering": [0.2],  # <-- Only has one value
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
                    "residual": [0.0, 0.0]
                },
                "blah": {
                    "smoldering": [0.2],  # <-- Only has one value
                    "total": [1.1, 1.34],
                    "flaming": [1.3, 1.14],
                    "residual": [0.0, 0.0]
                }
            }
        }
        with raises(ValueError) as e:
             EmissionsCalculator(LOOK_UP).calculate(['13','130'],
                consume_output, True)
        calculator = EmissionsCalculator(LOOK_UP, silent_fail=True)
        emissions = calculator.calculate(['13','130'], consume_output, True)
        assert 0 == len(emissions["litter-lichen-moss"].keys())  # <-- "litter" should have been skipped
        assert 1 == len(emissions["ground fuels"].keys())  # <-- "blah" should have been skipped
        expected = {
            "litter-lichen-moss": {},
            'ground fuels': {
                'basal accumulations': {
                    'flaming': {
                        'CO2': [188.67097873278277, 137.0622],
                        'CO': [17.490713281938074, 11.399999999999999]
                    },
                    'smoldering': {
                        'CO2': [20.963442081420308, 24.046000000000003],
                        'CO': [1.9434125868820082, 2.0]
                    },
                    'residual': {
                        'CO2': [9.1, 0.969],
                        'CO': [280.0, 36.0]
                    }
                }
            }
        }
        assert_results_are_approximately_equal(expected, emissions)

    def test_basic_one_fuel_bed(self):
        # 13's lookup
        # {
        #     'flame_smold_wf': {'CO2': 143.23,'CO': 14.0},
        #     'flame_smold_rx': {'CO2': 140.23,'CO': 13.0},
        #     'woody_rsc': {'CO2': 4.44,'CO': 140.0},
        #     'duff_rsc': {'CO2': 4.55,'CO': 142.0}
        # }
        consume_output = {
            "ground fuels": {
                "basal accumulations": {
                    "flaming": [1.1],
                    "smoldering": [2.2],
                    "residual": [3.3],
                    "total": [6.6]
                }
            }
        }
        calculator = EmissionsCalculator(LOOK_UP, silent_fail=True)
        emissions = calculator.calculate(['13'], consume_output, True)
        expected = {
            'ground fuels': {
                'basal accumulations': {
                    'flaming': {
                        'CO2': [154.253],
                        'CO': [14.3]
                    },
                    'smoldering': {
                        'CO2': [308.506],
                        'CO': [28.6]
                    },
                    'residual': {
                        'CO2': [15.015],
                        'CO': [468.6]
                    }
                }
            }
        }
        assert_results_are_approximately_equal(expected, emissions)

    def test_basic_two_fuel_beds(self):
        # TODO: implement
        pass

    def test_varying_chemical_species_two_fuel_beds(self):
        consume_output = {
            "litter-lichen-moss": {
                "litter": {
                    "smoldering": [0.2, 0.12],  # <-- Only has one value
                    "total": [1.4949327591400063, 0.34],
                    "flaming": [1.3454394832260057, 0.14],
                    "residual": [1.12, 0.32]
                }
            },
            "ground fuels": {
                "basal accumulations": {
                    "smoldering": [0.14949327591400063, 0.2],
                    "total": [1.4949327591400063, 1.34],
                    "flaming": [1.3454394832260057, 1.14],
                    "residual": [1.12, 0.32]
                }
            }
        }
        calculator = EmissionsCalculator(LOOK_UP_DIFFERING)
        emissions = calculator.calculate(['13','130'], consume_output, True)
        # TODO: hand compute these values to make sure they're correct
        expected = {
            'ground fuels': {
                'basal accumulations': {
                    'flaming': {
                        'CO2': [188.67097873278277, None],
                        'CO': [None, 11.399999999999999],
                        'PM2.5': [20.450680145035285, None]
                    },
                    'residual': {
                        'CO2': [5.096, None],
                        'CO': [None, 38.4]
                    },
                    'smoldering': {
                        'CO2': [20.963442081420308, None],
                        'CO': [None, 2.0],
                        'PM2.5': [2.2722977938928097, None]
                    }
                }
            },
            'litter-lichen-moss': {
                'litter': {
                    'flaming': {
                        'CO2': [188.67097873278277, None],
                        'CO': [None, 1.4000000000000001],
                        'PM2.5': [20.450680145035285, None]
                    },
                    'smoldering': {
                        'CO2': [20.963442081420308, None],
                        'CO': [None, 2.0],
                        'PM2.5': [2.2722977938928097, None]
                    }
                }
            }
        }
        assert_results_are_approximately_equal(expected, emissions)
