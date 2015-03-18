__author__      = "Joel Dubowy"
__copyright__   = "Copyright 2014, AirFire, PNW, USFS"

import logging
from collections import defaultdict

__all__ = [
    'EmissionsCalculator'
]

class EmissionsCalculator(object):

    def __init__(self, ef_lookup, **options):
        """EmissionsCalculator constructor

        Arguments:
         - ef_lookup - ef look-up dict or object (see note below)

        Options:
         - silent_fail - if any emissions calculations fails, or if subset of
           data is invalid, simply skip a exclude related emissions from output

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
        self._ef_lookup = ef_lookup
        self._options = options

    ERROR_MESSAGES = {
        "EF_LOOKUP_FAILURE": "Failed to look up emissions factors for %s",
        "MISSING_KEYS": "Missing keys in %s %s: %s",
        'DATA_LENGTH_MISMATCH': "Number of combustion values doesn't match "
            "number of fuelbeds / cover types"
    }

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

    ##
    ## Public Interface
    ##

    def calculate(self, ef_lookup_ids, consumption_dict, is_rx):
        """Calculates emissions given consume output

        Arguments
         - ef_lookup_ids -- array of either FCCS ids or FERA cover type ids,
            depending on the ef_lookup object passed to the constructor
         - consumption_dict -- dictionary of consume output  (see note below)
         - is_rx -- is a prescribed burn, as opposed to being a wild fire

        Note: consumption_dict is expected to be of the following form:

            {
                CATEGORY_1: {
                    SUB_CATEGORY_1: {
                        "smoldering": [...consumption values...],
                        "total": [...consumption values...],
                        "flaming": [...consumption values...],
                        "residual": [...consumption values...]
                    }
                    # ...other sub-categories...
                }
                # ...other categories...
            }

        For example:

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
                },
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
                "smoldering": [0.14949327591400063],
                "flaming": [1.3454394832260057],
                "residual": [0.0]
                /* possibly other keys, which are ignored */
            }
        """
        # TODO: make more fault tolerant

        # The folloing are set as intance attributes to reduce data passed in
        # method signatures.  Each time calculate is called, they are reset,
        # since calcualte could be called on a different set of fuelbed ids
        self.flaming_smoldering_key = 'flame_smold_rx' if is_rx else 'flame_smold_wf'
        self.ef_sets = self._get_ef_sets(ef_lookup_ids)
        self.num_fuelbeds = len(self.ef_sets)
        self.species_by_ef_group = self._species_sets_by_ef_group()

        emissions = {}
        for category, c_dict in consumption_dict.items():
            if not self._is_valid_category(category):
                continue

            e_c_dict = {}
            for sub_category, sc_dict in c_dict.items():
                # Sub-categories don't use the same residual EFs. Some use
                # woody_rsc, some use duff_rsc, and some have not residual
                # emissions
                rsc_key = self.RSC_KEYS.get(sub_category)
                # Initialize emissions sub-category dict
                e_sc_dict = self._initialize_emissions_inner_dict()
                for combustion_phase, cp_array in sc_dict.items():
                    if not self._is_valid_combustion_phase(combustion_phase,
                            cp_array):
                        continue
                    if 'residual' == combustion_phase and not rsc_key:
                        continue

                    k = rsc_key if 'residual' == combustion_phase else self.flaming_smoldering_key
                    for i in xrange(self.num_fuelbeds):
                        for species, ef in self.ef_sets[i][k].items():
                            e_sc_dict[combustion_phase][species][i] = ef * sc_dict[combustion_phase][i]

                e_c_dict[sub_category] = e_sc_dict
            if e_c_dict:
                emissions[category] = e_c_dict

        emissions['summary'] = self._compute_summary(emissions)

        return emissions

    ##
    ## Summary
    ##

    def _compute_summary(self, emissions):
        # TODO: compute emissions['summary'][CATEGORY] for all categories
        # and then compute emissions['summary']['totals'] from each of the
        # category summaries
        summary = {
            'total': self._initialize_emissions_inner_dict(include_total=True)
        }
        for category, e_c_dict in emissions.items():
            if not e_c_dict:
                # empty due to no valid subcategories
                continue

            summary[category] = self._initialize_emissions_inner_dict()
            for sub_category, e_sc_dict in e_c_dict.items():
                for phase, p_dict in e_sc_dict.items():
                    for species, s_list in p_dict.items():
                        for i in xrange(len(s_list)):
                            val = s_list[i]
                            summary[category][phase][species][i] += val
                            summary['total'][phase][species][i] += val
                            summary['total']['total'][species][i] += val
        return summary

    ##
    ## Emission Factors and Chemical Species
    ##

    def _get_ef_sets(self, ef_lookup_ids):
        try:
            ef_sets = [self._ef_lookup[eid] for eid in ef_lookup_ids]
        except KeyError, e:
            raise KeyError(self.ERROR_MESSAGES["EF_LOOKUP_FAILURE"] % (e))
        return ef_sets

    def _species_sets_by_ef_group(self):
        """Returns the cumulative set of checmical species accross all
        fuelbeds for each of the EF group.
        """
        return {
            'flaming_smoldering': self._species_set(self.flaming_smoldering_key),
            'residual': self._species_set('woody_rsc', 'duff_rsc')
        }

    def _species_set(self, *ef_group_keys):
        """Returns the cumulative set of checmical species accross all
        fuelbeds for a particular EF group.
        """
        species = []
        for ef_set in self.ef_sets:
            for ef_group_key in ef_group_keys:
                species.extend(ef_set[ef_group_key].keys())
        return set(species)

    ##
    ## Data Validation
    ##

    CATEGORIES_TO_SKIP = {
        'debug',
        'summary'
    }
    def _is_valid_category(self, category):
        return category not in self.CATEGORIES_TO_SKIP

    VALID_COMBUSTION_PHASES = set(['flaming', 'smoldering', 'residual'])
    def _is_valid_combustion_phase(self, combustion_phase, cp_array):
        if combustion_phase not in self.VALID_COMBUSTION_PHASES:
            return False

        if len(cp_array) != self.num_fuelbeds:
            msg = self.ERROR_MESSAGES['DATA_LENGTH_MISMATCH']
            if not self._options.get('silent_fail'):
                raise ValueError(msg)
            logging.info('%s -- Skipping' % (msg))
            return False
        return True

    ##
    ## Data Initialization
    ##

    def _initialize_emissions_inner_dict(self, include_total=False):
        """Initializes each combustion phase's species-specific emissions
        arrays to 0.0's so that, even if the ef-lookup object has different
        sets of chemical species for the various fuelbeds, each emissions
        array will be the same length).
        """
        fs_species = self.species_by_ef_group['flaming_smoldering']
        r_species = self.species_by_ef_group['residual']
        d = {
            'flaming': dict([(e, [0.0] * self.num_fuelbeds) for e in fs_species]),
            'smoldering': dict([(e, [0.0] * self.num_fuelbeds) for e in fs_species]),
            'residual': dict([(e, [0.0] * self.num_fuelbeds) for e in r_species])
        }
        if include_total:
            all_species = r_species.union(fs_species)
            d['total'] = dict([(e, [0.0] * self.num_fuelbeds) for e in all_species])
        return d
