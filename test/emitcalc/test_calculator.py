__author__      = "Joel Dubowy"
__copyright__   = "Copyright 2014, AirFire, PNW, USFS"

from py.test import raises

from emitcalc.calculator import EmissionsCalculator

LOOK_UP = {
    '13': {
        'flame_smold_wf': {'C02': 143.23,'CO': 14.0},
        'flame_smold_rx': {'C02': 140.23,'CO': 13.0},
        'woody_rsc': {'C02': 4.44,'CO': 140.0},
        'duff_rsc': {'C02': 4.55,'CO': 140.0}
    },
    '130': {
        'flame_smold_wf': {'C02': 123.23,'CO': 12.0},
        'flame_smold_rx': {'C02': 120.23,'CO': 10.0},
        'woody_rsc': {'C02': 3.23,'CO': 120.0},
        'duff_rsc': {'C02': 3.23,'CO': 120.0}
    }
}
LOOK_UP_DIFFERING = {
    '13': {
        'flame_smold_wf': {'CO': 14.0,'PM2.5': 15.2},
        'flame_smold_rx': {'C02': 140.23},
        'woody_rsc': {'CO': 140.0,'NM': 23.0},
        'duff_rsc': {'C02': 4.55}
    },
    '130': {
        'flame_smold_wf': {'C02': 123.23},
        'flame_smold_rx': {'CO': 10.0},
        'woody_rsc': {'C02': 3.23,'FDF': 2.32},
        'duff_rsc': {'CO': 120.0}
    }
}

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
                    "residual": [0.0, 0.0]
                }
            }
        }
        with raises(ValueError) as e:
             EmissionsCalculator(LOOK_UP).calculate(['13','130'],
                consume_output, True)
        calculator = EmissionsCalculator(LOOK_UP, silent_fail=True)
        emissions = calculator.calculate(['13','130'], consume_output, True)
        assert set(emissions.keys()) == {"ground fuels"}  # <-- "litter-lichen-moss" should have been skipped
        # TODO: assert values are correct

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
                }
            }
        }
        pass

    def test_basic_one_fuel_bed(self):

        pass

    def test_basic_two_fuel_beds(self):
        pass

    def test_varying_chemical_species_two_fuel_beds(self):
        pass
