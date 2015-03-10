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
                "total": [1.4949327591400063],
                "flaming": [1.3454394832260057],
                "residual": [0.0]
            }
        """
        # TODO: make more fault tolerant
        flaming_smoldering_key = 'flame_smold_rx' if is_rx else 'flame_smold_wf'

        emissions = {}
        try:
            ef_sets = [self._ef_lookup[eid] for eid in ef_lookup_ids]
        except KeyError, e:
            raise KeyError(self.ERROR_MESSAGES["EF_LOOKUP_FAILURE"] % (e))

        species_by_ef_group = self._species_sets_by_ef_group(ef_sets,
            flaming_smoldering_key)
        num_fuelbeds = len(ef_sets)

        for category, c_dict in consumption_dict.items():
            if not self._is_valid_category(category):
                continue

            e_c_dict = {}
            for sub_category, sc_dict in c_dict.items():
                if not self._is_valid_sub_category_dict(category,
                        sub_category, sc_dict, num_fuelbeds):
                    continue

                # Sub-categories don't use the same residual EFs. Some use
                # woody_rsc, some use duff_rsc, and some have not residual
                # emissions
                rsc_key = self.RSC_KEYS.get(sub_category)

                # Initialize emissions sub-category dict
                e_sc_dict = self._initialize_emissions_sub_category_dict(
                    species_by_ef_group, flaming_smoldering_key, rsc_key, num_fuelbeds)

                for i in xrange(num_fuelbeds):
                    for species, ef in ef_sets[i][flaming_smoldering_key].items():
                        e_sc_dict['flaming'][species][i] = ef * sc_dict['flaming'][i]
                        e_sc_dict['smoldering'][species][i] = ef * sc_dict['smoldering'][i]
                    if rsc_key:
                        for species, ef in ef_sets[i][rsc_key].items():
                            e_sc_dict['residual'][species][i] = ef * sc_dict['residual'][i]

                e_c_dict[sub_category] = e_sc_dict
            if e_c_dict:
                emissions[category] = e_c_dict

        emissions['summary'] = self._compute_summary(emissions, species_by_ef_group, ef_sets, flaming_smoldering_key)

        return emissions

    def _compute_summary(self, emissions, species_by_ef_group, ef_sets, flaming_smoldering_key):
        # TODO: compute emissions['summary'][CATEGORY] for all categories
        # and then compute emissions['summary']['totals'] from each of the
        # category summaries
        species_by_ef_group = self._species_sets_by_ef_group(ef_sets,
            flaming_smoldering_key)
        num_fuelbeds = len(ef_sets)
        summary = {
            'total': self._initialize_emissions_sub_category_dict(
                    species_by_ef_group, flaming_smoldering_key,
                    ['woody_rsc', 'duff_rsc'], num_fuelbeds)
        }
        for category, e_c_dict in emissions.items():
            if not e_c_dict:
                # empty due to no valid subcategories
                continue

            summary[category] = self._initialize_emissions_sub_category_dict(
                species_by_ef_group, flaming_smoldering_key,
                ['woody_rsc', 'duff_rsc'], num_fuelbeds)
            for sub_category, e_sc_dict in e_c_dict.items():
                for phase, p_dict in e_sc_dict.items():
                    for species, s_list in p_dict.items():
                        for i in xrange(len(s_list)):
                            val = s_list[i]
                            if val is not None:
                                if summary[category][phase][species][i] is None:
                                    summary[category][phase][species][i] = 0.0
                                if summary['total'][phase][species][i] is None:
                                    summary['total'][phase][species][i] = 0.0
                                summary[category][phase][species][i] += val
                                summary['total'][phase][species][i] += val
        return summary

    def _species_sets_by_ef_group(self, ef_sets, flaming_smoldering_key):
        """Returns the cumulative set of checmical species accross all
        fuelbeds for each of the EF group.
        """
        return {
            flaming_smoldering_key: self._species_set(ef_sets, flaming_smoldering_key),
            'woody_rsc': self._species_set(ef_sets, 'woody_rsc'),
            'duff_rsc': self._species_set(ef_sets, 'duff_rsc')
        }

    def _species_set(self, ef_sets, ef_group_key):
        """Returns the cumulative set of checmical species accross all
        fuelbeds for a particular EF group.
        """
        return set(reduce(lambda a,b: a+b, [efs[ef_group_key].keys() for efs in ef_sets]))


    CATEGORIES_TO_SKIP = {
        'debug',
        'summary'
    }

    def _is_valid_category(self, category):
        return category not in self.CATEGORIES_TO_SKIP

    COMBUSTION_PHASES = set(['flaming', 'smoldering', 'residual'])

    def _is_valid_sub_category_dict(self, category, sub_category, sc_dict,
            num_fuelbeds):
        # Make sure sc_dict is complete
        missing_keys = self.COMBUSTION_PHASES.difference(sc_dict.keys())
        if missing_keys:
            msg = self.ERROR_MESSAGES['MISSING_KEYS'] % (
                category, sub_category, missing_keys)
            if not self._options.get('silent_fail'):
                raise ValueError(msg)
            logging.info('%s -- Skipping' % (msg))
            return False

        # Make sure each cumbustion phase array has as many values as there are fuelbeds
        if 1 != len(set([num_fuelbeds] + [len(sc_dict[e]) for e in self.COMBUSTION_PHASES])):
            msg = self.ERROR_MESSAGES['DATA_LENGTH_MISMATCH']
            if not self._options.get('silent_fail'):
                raise ValueError(msg)
            logging.info('%s -- Skipping' % (msg))
            return False

        return True


    def _initialize_emissions_sub_category_dict(self, species_by_ef_group,
            flaming_smoldering_key, rsc_key, num_fuelbeds):
        """Initializes each combustion phase's species-specific emissions
        arrays to None's so that, even if the ef-lookup object has different
        sets of chemical species for the various fuelbeds, each emissions
        array will be the same length (with None's holding the place when
        a fuelbed lacks a particular species' EF).
        """
        fs_species = species_by_ef_group[flaming_smoldering_key]
        e_sc_dict = {
            'flaming': dict([(e, [None] * num_fuelbeds) for e in fs_species]),
            'smoldering': dict([(e, [None] * num_fuelbeds) for e in fs_species])
        }
        if rsc_key:
            if hasattr(rsc_key, 'pop'):
                r_species = [species_by_ef_group[k] for k in rsc_key]
                r_species = set(reduce(lambda a,b: [a.add(e) for e in b] and a, r_species, set()))
            else:
                r_species = species_by_ef_group[rsc_key]
            e_sc_dict['residual'] = dict([(e, [None] * num_fuelbeds) for e in r_species])
        return e_sc_dict
