__author__      = "Joel Dubowy"
__copyright__   = "Copyright 2014, AirFire, PNW, USFS"

from collections import defaultdict

__all__ = [
    'EmissionsCalculator'
]

class EmissionsCalculator(object):
    def __init__(self, ef_lookup):
        """EmissionsCalculator constructor

        Arguments:
         - ef_lookup - ef look-up dict or object (see note below)

        Note:  ef_lookup can be a simple dict or something like an instance
        of fccs2ef.lookup.Fccs2Ef.  It just needs to support __getitem___, and
        given an FCCS id or covertype id (or whatever id you're using to look up
        emissions factors), return an dictionary of the following form:

            {
                'flame_smold_wf': { 'CH3CH2OH': 123.23, ... },
                'flame_smold_rx': {...},
                'woody_rsc': {...},
                'duff_rsc': {...}
            }

        """
        self.ef_lookup = ef_lookup


    # TODO: check these!!!
    # TODO: expect different keys???
    RSC_KEYS = {
        "100-hr fuels": 'woody_rsc',
        "1000-hr fuels sound": 'woody_rsc',
        "1000-hr fuels rotten": 'woody_rsc',
        "10k+-hr fuels rotten": 'woody_rsc',
        "10k+-hr fuels sound": 'woody_rsc',
        "10000-hr fuels rotten": 'woody_rsc',
        "-hr fuels sound": 'woody_rsc',
        "stumps rotten": 'woody_rsc',
        "stumps lightered": 'woody_rsc',
        "duff lower": 'duff_rsc',
        "duff upper": 'duff_rsc',
        "basal accumulations": 'duff_rsc',
        "squirrel middens": 'duff_rsc'
    }

    def calculate(self, ef_lookup_id, consumption_dict, is_rx):
        """Calculates emissions given consume output

        Arguments
         - ef_lookup_id -- this could be either FCCS id or FERA cover type id,
            depending on the ef_lookup object passed to the constructor
         - consumption_dict -- dictionary of consume output  (see note below)
         - is_rx -- is a prescribed burn, as opposed to being a wild fire

        Note: consumption_dict is expected to be of the following form:

        # TODO: modify this form, mostly using different keys ???

            {
                "litter-lichen-moss": {
                    "litter": { ... },
                    "lichen": { ... },
                    "moss": { ... }
                },
                "nonwoody": {
                    "primary dead": { ... },
                    "secondary live": { ... },
                    "primary live": { ... },
                    "secondary dead": { ... }
                },
                "shrub": {
                    "primary dead": { ... },
                    "secondary live": { ... },
                    "primary live": { ... },
                    "secondary dead": { ... }
                },
                "ground fuels": {
                    "duff lower": { ... },
                    "basal accumulations": { ... },
                    "duff upper": { ... },
                    "squirrel middens": { ... }
                },
                "woody fuels": {
                    "1000-hr fuels rotten": { ... },
                    "1000-hr fuels sound": { ... },
                    "stumps rotten": { ... },
                    "100-hr fuels": { ... },
                    "1-hr fuels": { ... },
                    "piles": { ... },
                    "stumps lightered": { ... },
                    "10k+-hr fuels sound": { ... },
                    "10000-hr fuels rotten": { ... },
                    "10000-hr fuels sound": { ... },
                    "10k+-hr fuels rotten": { ... },
                    "stumps sound": { ... },
                    "10-hr fuels": { ... }
                },
                "canopy": {
                    "snags class 3": { ... },
                    "snags class 1 foliage": { ... },
                    "ladder fuels": { ... },
                    "snags class 1 wood": { ... },
                    "snags class 2": { ... },
                    "understory": { ... },
                    "overstory": { ... },
                    "midstory": { ... },
                    "snags class 1 no foliage": { ... }
                }
                "summary": {
                    "litter-lichen-moss": { ...},
                    "nonwoody": { ... },
                    "shrub": { ... },
                    "woody fuels": { ...},
                    "ground fuels": { ... },
                    "canopy": { ... },
                    "total": { ... }
                }
            }

        where each inner-most dict, { ... }, is of the form:

            {
                "smoldering": 0.14949327591400063,
                "total": 1.4949327591400063,
                "flaming": 1.3454394832260057,
                "residual": 0.0
            }

        """
        # TODO: make more fault tolerant
        flaming_smoldering_key = 'flame_smold_rx' if is_rx else 'flame_smold_wf'
        emissions = {}
        efs = self.ef_lookup[ef_lookup_id]
        for category, c_dict in consumption_dict.items():
            emissions[category] = {}
            for sub_category, sc_dict in c_dict.items():
                emissions[category][sub_category] = {
                    'flaming': {},
                    'smoldering': {}
                }
                for species, ef in efs[flaming_smoldering_key].items():
                    emissions[category][sub_category]['flaming'][species] = ef * sc_dict['flaming']
                    emissions[category][sub_category]['smoldering'][species] = ef * sc_dict['smoldering']
                rsc_key = self.RSC_KEYS.get(sub_category)
                if rsc_key:
                    emissions[category][sub_category].update(residual={})
                    for species, ef in efs[rsc_key].items():
                        emissions[category][sub_category]['residual'][species] = ef * sc_dict['residual']

        return dict(emissions)
