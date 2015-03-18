__author__      = "Joel Dubowy"
__copyright__   = "Copyright 2014, AirFire, PNW, USFS"

import copy
from numpy.testing import assert_approx_equal
from py.test import raises#, mark

from emitcalc.calculator import EmissionsCalculator

# Test CONSUME output

BASAL_ACCUMULATIONS_RX_13_130_CONSUME_OUT = {
    "flaming": [1.345, 1.14],
    "smoldering": [0.149, 0.2],
    "residual": [2.0, 0.3],
    "total": [1.4949, 1.34]
}

BASAL_ACCUMULATIONS_RX_13_CONSUME_OUT = dict([(k, v[:1]) for k,v in
    BASAL_ACCUMULATIONS_RX_13_130_CONSUME_OUT.items()])

BASAL_ACCUMULATIONS_LEN_1_FLAMING_RX_13_130_CONSUME_OUT = copy.deepcopy(
    BASAL_ACCUMULATIONS_RX_13_130_CONSUME_OUT)
BASAL_ACCUMULATIONS_LEN_1_FLAMING_RX_13_130_CONSUME_OUT['flaming'].pop()

BASAL_ACCUMULATIONS_NO_FLAMING_RX_13_130_CONSUME_OUT = copy.deepcopy(
    BASAL_ACCUMULATIONS_LEN_1_FLAMING_RX_13_130_CONSUME_OUT)
BASAL_ACCUMULATIONS_NO_FLAMING_RX_13_130_CONSUME_OUT.pop('flaming')

LITTER_RX_13_130_CONSUME_OUT = {
    "flaming": [1.3, 0.14],
    "smoldering": [0.2, 0.12],
    "residual": [1.12, 0.32],
    "total": [1.2, 0.34]
}

DUMMY_SUMMARY_CONSUME_OUT = {
    "flaming": [13.3, 30.14],
    "smoldering": [4.2, 0.34312],
    "residual": [1.13432, 0.3232],
    "total": [12.2, 0.334]
}

# Test lookup dicts

LOOK_UP = {
    '13': {
        'flame_smold_wf': {'CO2': 143.23, 'CO': 14.0},
        'flame_smold_rx': {'CO2': 140.23, 'CO': 13.0},
        'woody_rsc': {'CO2': 4.44, 'CO': 140.0},
        'duff_rsc': {'CO2': 4.55, 'CO': 140.0}
    },
    '130': {
        'flame_smold_wf': {'CO2': 123.23, 'CO': 12.0},
        'flame_smold_rx': {'CO2': 120.23, 'CO': 10.0},
        'woody_rsc': {'CO2': 3.23, 'CO': 120.0},
        'duff_rsc': {'CO2': 3.23, 'CO': 120.0}
    }
}
LOOK_UP_DIFFERING = {
    '13': {
        'flame_smold_wf': {'CO': 14.0, 'PM10': 15.2},
        'flame_smold_rx': {'CO2': 140.23, 'PM2.5': 15.2},
        'woody_rsc': {'CO': 140.0, 'NM': 23.0},
        'duff_rsc': {'CO2': 4.55}
    },
    '130': {
        'flame_smold_wf': {'CO2': 123.23},
        'flame_smold_rx': {'CO': 10.0},
        'woody_rsc': {'CO2': 3.23, 'FDF': 2.32},
        'duff_rsc': {'CO': 120.0}
    }
}

# Expected emissions
# Note: These were hand-calculated from the consume output and expected
# emissions listed above

BASAL_ACCUMULATIONS_RX_13_130_NORMAL_LOOKUP_EMISSIONS_EXPECTED = {
    'flaming': {
        'CO2': [188.60934999999998, 137.0622],
        'CO': [17.485, 11.4]
    },
    'smoldering': {
        'CO2': [20.89427, 24.046000000000003],
        'CO': [1.9369999999999998, 2.0]
    },
    'residual': {
        'CO2': [9.1, 0.969],
        'CO': [280.0, 36.0]
    }
}
TOTAL_BASAL_ACCUMULATIONS_RX_13_130_NORMAL_LOOKUP_EMISSIONS_EXPECTED = copy.deepcopy(
    BASAL_ACCUMULATIONS_RX_13_130_NORMAL_LOOKUP_EMISSIONS_EXPECTED)
TOTAL_BASAL_ACCUMULATIONS_RX_13_130_NORMAL_LOOKUP_EMISSIONS_EXPECTED["total"] = {
    'CO2': [218.60361999999998, 162.0772],
    'CO': [299.422, 49.4]
}

BASAL_ACCUMULATIONS_RX_13_NORMAL_LOOKUP_EMISSIONS_EXPECTED = dict([
    (k, dict([(k2, v2[:1]) for k2,v2 in  v.items()]))
        for k,v in BASAL_ACCUMULATIONS_RX_13_130_NORMAL_LOOKUP_EMISSIONS_EXPECTED.items()
])
TOTAL_BASAL_ACCUMULATIONS_RX_13_NORMAL_LOOKUP_EMISSIONS_EXPECTED = dict([
    (k, dict([(k2, v2[:1]) for k2,v2 in  v.items()]))
        for k,v in TOTAL_BASAL_ACCUMULATIONS_RX_13_130_NORMAL_LOOKUP_EMISSIONS_EXPECTED.items()
])

BASAL_ACCUMULATIONS_NO_FLAMING_RX_13_130_NORMAL_LOOKUP_EMISSIONS_EXPECTED = copy.deepcopy(
    BASAL_ACCUMULATIONS_RX_13_130_NORMAL_LOOKUP_EMISSIONS_EXPECTED)
for s, sa in BASAL_ACCUMULATIONS_NO_FLAMING_RX_13_130_NORMAL_LOOKUP_EMISSIONS_EXPECTED['flaming'].items():
    BASAL_ACCUMULATIONS_NO_FLAMING_RX_13_130_NORMAL_LOOKUP_EMISSIONS_EXPECTED['flaming'][s] = len(sa) * [0.0]
TOTAL_BASAL_ACCUMULATIONS_NO_FLAMING_RX_13_130_NORMAL_LOOKUP_EMISSIONS_EXPECTED = copy.deepcopy(
    BASAL_ACCUMULATIONS_NO_FLAMING_RX_13_130_NORMAL_LOOKUP_EMISSIONS_EXPECTED)
TOTAL_BASAL_ACCUMULATIONS_NO_FLAMING_RX_13_130_NORMAL_LOOKUP_EMISSIONS_EXPECTED["total"] = {
    'CO2': [29.99427, 25.015000000000004],
    'CO': [281.9369999999999998, 38.0]
}

BASAL_ACCUMULATIONS_RX_13_130_DIFFERING_LOOKUP_EMISSIONS_EXPECTED = {
    'flaming': {
        'CO2': [188.60934999999998, 0.0],
        'CO': [0.0, 11.4],
        'PM2.5': [20.444, 0.0]
    },
    'smoldering': {
        'CO2': [20.89427, 0.0],
        'CO': [0.0, 2.0],
        'PM2.5': [2.2647999999999997, 0.0]
    },
    'residual': {
        'CO2': [9.1, 0.0],
        'CO': [0.0, 36.0],
        'NM': [0.0, 0.0],
        'FDF': [0.0, 0.0]
    }
}
TOTAL_BASAL_ACCUMULATIONS_RX_13_130_DIFFERING_LOOKUP_EMISSIONS_EXPECTED = copy.deepcopy(
    BASAL_ACCUMULATIONS_RX_13_130_DIFFERING_LOOKUP_EMISSIONS_EXPECTED)
TOTAL_BASAL_ACCUMULATIONS_RX_13_130_DIFFERING_LOOKUP_EMISSIONS_EXPECTED["total"] = {
    'CO2': [218.60361999999998, 0.0],
    'CO': [0.0, 49.4],
    'NM': [0.0, 0.0],
    'FDF': [0.0, 0.0],
    'PM2.5': [22.7088, 0.0]
}

LITTER_RX_13_130_DIFFERING_LOOKUP_EMISSIONS_EXPECTED = {
    'flaming': {
        'CO2': [182.299, 0.0],
        'CO': [0.0, 1.4],
        'PM2.5': [19.759999999999998, 0.0]
    },
    'smoldering': {
        'CO2': [28.046, 0.0],
        'CO': [0.0, 1.2],
        'PM2.5': [3.04, 0.0]
    },
    'residual': {
        'CO2': [0.0, 0.0],
        'CO': [0.0, 0.0],
        'NM': [0.0, 0.0],
        'FDF': [0.0, 0.0]
    }
}
TOTAL_LITTER_RX_13_130_DIFFERING_LOOKUP_EMISSIONS_EXPECTED = copy.deepcopy(
    LITTER_RX_13_130_DIFFERING_LOOKUP_EMISSIONS_EXPECTED)
TOTAL_LITTER_RX_13_130_DIFFERING_LOOKUP_EMISSIONS_EXPECTED["total"] = {
    'CO2': [210.345, 0.0],
    'CO': [0.0, 2.6],
    'NM': [0.0, 0.0],
    'FDF': [0.0, 0.0],
    'PM2.5': [22.799999999999997, 0.0]
}

TOTAL_BASAL_ACCUMULATIONS_PLUS_LITTER_RX_13_130_DIFFERING_LOOKUP_EMISSIONS_EXPECTED = {
    'flaming': {
        'CO2': [370.90834999999998, 0.0],
        'CO': [0.0, 12.8],
        'PM2.5': [40.20399999999999, 0.0]
    },
    'smoldering': {
        'CO2': [48.94027, 0.0],
        'CO': [0.0, 3.2],
        'PM2.5': [5.3047999999999997, 0.0]
    },
    'residual': {
        'CO2': [9.1, 0.0],
        'CO': [0.0, 36.0],
        'NM': [0.0, 0.0],
        'FDF': [0.0, 0.0]
    },
    'total': {
        'CO2': [428.94862, 0.0],
        'CO': [0.0, 52.0],
        'NM': [0.0, 0.0],
        'FDF': [0.0, 0.0],
        'PM2.5': [45.508799999999994, 0.0]
    }
}

LITTER_RX_13_130_DIFFERING_LOOKUP_WHITELIST_CO_PM25_FDF_EMISSIONS_EXPECTED = copy.deepcopy(
    LITTER_RX_13_130_DIFFERING_LOOKUP_EMISSIONS_EXPECTED)
for k,v in LITTER_RX_13_130_DIFFERING_LOOKUP_WHITELIST_CO_PM25_FDF_EMISSIONS_EXPECTED.items():
    for k2 in v.keys():
        if k2 not in ['CO','PM2.5','FDF']:
            v.pop(k2)

BASAL_ACCUMULATIONS_RX_13_130_DIFFERING_LOOKUP_WHITELIST_CO_PM25_FDF_EMISSIONS_EXPECTED = copy.deepcopy(
    BASAL_ACCUMULATIONS_RX_13_130_DIFFERING_LOOKUP_EMISSIONS_EXPECTED)
for k,v in BASAL_ACCUMULATIONS_RX_13_130_DIFFERING_LOOKUP_WHITELIST_CO_PM25_FDF_EMISSIONS_EXPECTED.items():
    for k2 in v.keys():
        if k2 not in ['CO','PM2.5','FDF']:
            v.pop(k2)

TOTAL_BASAL_ACCUMULATIONS_PLUS_LITTER_RX_13_130_DIFFERING_LOOKUP_WHITELIST_CO_PM25_FDF_EMISSIONS_EXPECTED = copy.deepcopy(
    TOTAL_BASAL_ACCUMULATIONS_PLUS_LITTER_RX_13_130_DIFFERING_LOOKUP_EMISSIONS_EXPECTED)
for k,v in TOTAL_BASAL_ACCUMULATIONS_PLUS_LITTER_RX_13_130_DIFFERING_LOOKUP_WHITELIST_CO_PM25_FDF_EMISSIONS_EXPECTED.items():
    for k2 in v.keys():
        if k2 not in ['CO','PM2.5','FDF']:
            v.pop(k2)

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
                        print "expected[%s][%s][%s][%s][%s][%s] vs actual[%s][%s][%s][%s][%s][%s]" % (
                            c,sc,cp,s,i,expected[c][sc][cp][s][i],
                            c,sc,cp,s,i,actual[c][sc][cp][s][i])
                        if expected[c][sc][cp][s][i] is None:
                            assert None == actual[c][sc][cp][s][i]
                        else:
                            # first argument in assert_approx_equal is actual,
                            # second is epected (it doesn't matter except that
                            # error message will be misleading if order is reversed)
                            assert_approx_equal(
                                actual[c][sc][cp][s][i],
                                expected[c][sc][cp][s][i],
                                significant=8  # arbitrarily chose 8
                            )



class TestEmissionsCalculator:

    # Error cases that raise exception:

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
            EmissionsCalculator(LOOK_UP).calculate(['13sdf', '130'],
                consume_output, True)

    # Error cases that raise exception unless silent_fail=True:

    def test_differing_number_of_consumption_values(self):
        consume_output = {
            "ground fuels": {
                "basal accumulations": BASAL_ACCUMULATIONS_LEN_1_FLAMING_RX_13_130_CONSUME_OUT
            }
        }
        with raises(ValueError) as e:
             EmissionsCalculator(LOOK_UP).calculate(['13', '130'],
                consume_output, True)
        calculator = EmissionsCalculator(LOOK_UP, silent_fail=True)
        emissions = calculator.calculate(['13', '130'], consume_output, True)
        # Flaming dict should have been skipped, so
        expected = {
            'ground fuels': {
                'basal accumulations': BASAL_ACCUMULATIONS_NO_FLAMING_RX_13_130_NORMAL_LOOKUP_EMISSIONS_EXPECTED
            },
            "summary": {
                "ground fuels": BASAL_ACCUMULATIONS_NO_FLAMING_RX_13_130_NORMAL_LOOKUP_EMISSIONS_EXPECTED,
                "total": TOTAL_BASAL_ACCUMULATIONS_NO_FLAMING_RX_13_130_NORMAL_LOOKUP_EMISSIONS_EXPECTED
            }

        }
        assert_results_are_approximately_equal(expected, emissions)

    # Error situations where some input data is ignored

    def test_missing_combustion_phase_keys(self):
        consume_output = {
            "ground fuels": {
                "basal accumulations": BASAL_ACCUMULATIONS_NO_FLAMING_RX_13_130_CONSUME_OUT
            }
        }
        calculator = EmissionsCalculator(LOOK_UP)
        emissions = calculator.calculate(['13', '130'], consume_output, True)
        expected = {
            'ground fuels': {
                'basal accumulations': BASAL_ACCUMULATIONS_NO_FLAMING_RX_13_130_NORMAL_LOOKUP_EMISSIONS_EXPECTED
            },
            "summary": {
                "ground fuels": BASAL_ACCUMULATIONS_NO_FLAMING_RX_13_130_NORMAL_LOOKUP_EMISSIONS_EXPECTED,
                "total": TOTAL_BASAL_ACCUMULATIONS_NO_FLAMING_RX_13_130_NORMAL_LOOKUP_EMISSIONS_EXPECTED
            }
        }
        assert_results_are_approximately_equal(expected, emissions)

    # Valid data cases

    def test_basic_one_fuel_bed(self):
        consume_output = {
            "ground fuels": {
                "basal accumulations": BASAL_ACCUMULATIONS_RX_13_CONSUME_OUT,
            },
            "debug": {  # <-- ignored
                "foo": "bar"
            },
             "summary": {  # <-- ignored
                "ground fuels": DUMMY_SUMMARY_CONSUME_OUT,
                "total": DUMMY_SUMMARY_CONSUME_OUT
            }
        }
        calculator = EmissionsCalculator(LOOK_UP, silent_fail=True)
        emissions = calculator.calculate(['13'], consume_output, True)
        expected = {
            'ground fuels': {
                'basal accumulations': BASAL_ACCUMULATIONS_RX_13_NORMAL_LOOKUP_EMISSIONS_EXPECTED
            },
            'summary': {
                'ground fuels': BASAL_ACCUMULATIONS_RX_13_NORMAL_LOOKUP_EMISSIONS_EXPECTED,
                'total': TOTAL_BASAL_ACCUMULATIONS_RX_13_NORMAL_LOOKUP_EMISSIONS_EXPECTED
            }
        }
        assert_results_are_approximately_equal(expected, emissions)

    def test_basic_two_fuel_beds(self):
        consume_output = {
            "ground fuels": {
                "basal accumulations": BASAL_ACCUMULATIONS_RX_13_130_CONSUME_OUT
            },
            "debug": {  # <-- ignored
                "foo": "bar"
            },
            "summary": {  # <-- ignored
                "ground fuels": DUMMY_SUMMARY_CONSUME_OUT,
                "total": DUMMY_SUMMARY_CONSUME_OUT
            }
        }
        calculator = EmissionsCalculator(LOOK_UP, silent_fail=True)
        emissions = calculator.calculate(['13', '130'], consume_output, True)
        expected = {
            'ground fuels': {
                'basal accumulations': BASAL_ACCUMULATIONS_RX_13_130_NORMAL_LOOKUP_EMISSIONS_EXPECTED
            },
            'summary': {
                'ground fuels': BASAL_ACCUMULATIONS_RX_13_130_NORMAL_LOOKUP_EMISSIONS_EXPECTED,
                'total': TOTAL_BASAL_ACCUMULATIONS_RX_13_130_NORMAL_LOOKUP_EMISSIONS_EXPECTED
            }
        }
        assert_results_are_approximately_equal(expected, emissions)

    def test_varying_chemical_species_two_fuel_beds(self):
        consume_output = {
            "litter-lichen-moss": {
                "litter": LITTER_RX_13_130_CONSUME_OUT
            },
            "ground fuels": {
                "basal accumulations": BASAL_ACCUMULATIONS_RX_13_130_CONSUME_OUT
            },
            "debug": {  # <-- ignored
                "foo": "bar"
            },
            "summary": {  # <-- ignored
                "litter-lichen-moss": DUMMY_SUMMARY_CONSUME_OUT,
                "ground fuels": DUMMY_SUMMARY_CONSUME_OUT,
                "total": DUMMY_SUMMARY_CONSUME_OUT
            }
        }
        calculator = EmissionsCalculator(LOOK_UP_DIFFERING)
        emissions = calculator.calculate(['13', '130'], consume_output, True)
        # TODO: hand compute these values to make sure they're correct
        expected = {
            'ground fuels': {
                'basal accumulations': BASAL_ACCUMULATIONS_RX_13_130_DIFFERING_LOOKUP_EMISSIONS_EXPECTED
            },
            'litter-lichen-moss': {
                'litter': LITTER_RX_13_130_DIFFERING_LOOKUP_EMISSIONS_EXPECTED
            },
            "summary": {
                "ground fuels": BASAL_ACCUMULATIONS_RX_13_130_DIFFERING_LOOKUP_EMISSIONS_EXPECTED,
                "litter-lichen-moss": LITTER_RX_13_130_DIFFERING_LOOKUP_EMISSIONS_EXPECTED,
                "total": TOTAL_BASAL_ACCUMULATIONS_PLUS_LITTER_RX_13_130_DIFFERING_LOOKUP_EMISSIONS_EXPECTED
            }

        }
        assert_results_are_approximately_equal(expected, emissions)

    def test_varying_chemical_species_two_fuel_beds_species_whitelist(self):
        consume_output = {
            "litter-lichen-moss": {
                "litter": LITTER_RX_13_130_CONSUME_OUT
            },
            "ground fuels": {
                "basal accumulations": BASAL_ACCUMULATIONS_RX_13_130_CONSUME_OUT
            },
            "debug": {  # <-- ignored
                "foo": "bar"
            },
            "summary": {  # <-- ignored
                "litter-lichen-moss": DUMMY_SUMMARY_CONSUME_OUT,
                "ground fuels": DUMMY_SUMMARY_CONSUME_OUT,
                "total": DUMMY_SUMMARY_CONSUME_OUT
            }
        }
        calculator = EmissionsCalculator(LOOK_UP_DIFFERING, species=['CO', 'PM2.5', 'FDF'])
        emissions = calculator.calculate(['13', '130'], consume_output, True)
        # TODO: hand compute these values to make sure they're correct
        expected = {
            'ground fuels': {
                'basal accumulations': BASAL_ACCUMULATIONS_RX_13_130_DIFFERING_LOOKUP_WHITELIST_CO_PM25_FDF_EMISSIONS_EXPECTED
            },
            'litter-lichen-moss': {
                'litter': LITTER_RX_13_130_DIFFERING_LOOKUP_WHITELIST_CO_PM25_FDF_EMISSIONS_EXPECTED
            },
            "summary": {
                "ground fuels": BASAL_ACCUMULATIONS_RX_13_130_DIFFERING_LOOKUP_WHITELIST_CO_PM25_FDF_EMISSIONS_EXPECTED,
                "litter-lichen-moss": LITTER_RX_13_130_DIFFERING_LOOKUP_WHITELIST_CO_PM25_FDF_EMISSIONS_EXPECTED,
                "total": TOTAL_BASAL_ACCUMULATIONS_PLUS_LITTER_RX_13_130_DIFFERING_LOOKUP_WHITELIST_CO_PM25_FDF_EMISSIONS_EXPECTED
            }

        }
        assert_results_are_approximately_equal(expected, emissions)

    # TODO: test case where summary sums float with None (and thus skips 'None')
