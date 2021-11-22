__author__      = "Joel Dubowy"

import logging
from collections import defaultdict
from functools import reduce

__all__ = [
    'EmissionsCalculator'
]

class InvalidConsumptionDataError(ValueError):
    pass

class EmissionsCalculator(object):

    def __init__(self, ef_lookup_objects, **options):
        """EmissionsCalculator constructor

        Args:
         - ef_lookup_objects -- either an array of look-up objects or a
           single one

        Options:
         - silent_fail - if any emissions calculations fails, or if subset of
           data is invalid, simply skip a exclude related emissions from output
         - species - whitelist of species to compute emissions for

        Notes:
         - each look-up object must support the following interface:
           get(phase=PHASE, fuel_category=FUEL_CATEGORY, species=SPECIES)
           species(phase)
         - Note: self._num_ef_look_up_objects is used later to set
           self._num_fuelbeds. If self._num_ef_look_up_objects is not None,
           then self._num_fuelbeds is set to its value. Otherwise, a None value
           indicates that we need to determine the number of fuelbeds from the
           length of the inner data arrays. self._num_fuelbeds must be set on
           each call to calcualte, since the number of fuelbeds in the
           consumption data can vary from call to call (though, only in the
           case where a single lookup object is used for all fuelbeds)
        """
        self._species_whitelist = set(options.get('species', []))
        self._silent_fail = options.get('silent_fail')
        self._ef_lookup_objects = ef_lookup_objects
        if not hasattr(self._ef_lookup_objects, 'species'):
            self._num_ef_look_up_objects = len(self._ef_lookup_objects)
        else:
            self._num_ef_look_up_objects = None
        self._set_output_species()

    ERROR_MESSAGES = {
        "INVALID_INPUT_TOP_LEVEL": "Invalid consumption data",
        "INVALID_INPUT_CATEGORY": "Invalid consumption data category - %s",
        "INVALID_INPUT_SUB_CATEGORY": "Invalid consumption data sub-category - %s > %s",
        'INVALID_INPUT_DATA_LENGTH_MISMATCH': "Number of combustion values "
            "doesn't match number of fuelbeds / cover types - %s > %s > %s "
    }

    ##
    ## Public Interface
    ##

    def calculate(self, consumption_dict):
        """Calculates emissions given consume output

        Arguments
         - consumption_dict -- dictionary of consume output  (see note below)

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
        self._num_fuelbeds = self._num_ef_look_up_objects
        self._prune_and_validate(consumption_dict)

        self.emissions_factors = {}  # for reference by client
        emissions = {}
        for category, c_dict in list(consumption_dict.items()):
            e_c_dict = {}
            efs_c_dict = {}
            for sub_category, sc_dict in list(c_dict.items()):
                e_sc_dict = self._initialize_emissions_inner_dict()
                efs_sc_dict = self._initialize_emissions_inner_dict()
                for phase, cp_array in list(sc_dict.items()):
                    for i in range(self._num_fuelbeds):
                        look_up = self._ef_lookup_object(i)
                        for species in self._output_species_set(i)[phase]:
                            ef = look_up.get(phase=phase,
                                fuel_category=category,
                                fuel_sub_category=sub_category,
                                species=species)
                            # 'ef' may sometimes be undefined - e.g. for the
                            # 'residual' phase for certain fuel categories
                            # set to zero in these cases
                            ef = ef or 0.0
                            efs_sc_dict[phase][species] = ef # ef will be the same for each fuelbed
                            e_sc_dict[phase][species][i] = ef * sc_dict[phase][i]
                            # logging.debug('%s > %s > %s > %s: %s * %s = %s',
                            #     category, sub_category, phase,
                            #     species, ef, sc_dict[phase][i],
                            #     e_sc_dict[phase][species][i])

                e_c_dict[sub_category] = e_sc_dict
                efs_c_dict[sub_category] = efs_sc_dict
            if e_c_dict:
                emissions[category] = e_c_dict
                self.emissions_factors[category] = efs_c_dict

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
        for category, e_c_dict in list(emissions.items()):
            if not e_c_dict:
                # empty due to no valid subcategories
                continue

            summary[category] = self._initialize_emissions_inner_dict()
            for sub_category, e_sc_dict in list(e_c_dict.items()):
                for phase, p_dict in list(e_sc_dict.items()):
                    for species, s_list in list(p_dict.items()):
                        for i in range(len(s_list)):
                            val = s_list[i]
                            summary[category][phase][species][i] += val
                            summary['total'][phase][species][i] += val
                            summary['total']['total'][species][i] += val
        return summary

    ##
    ## Emission Factors and Chemical Species
    ##

    # Note: these three methods - _ef_lookup_object, _output_species_set, and
    # _set_output_species - are a bit hacky to handle either one look-up per
    # fuelbed or one for all

    def _ef_lookup_object(self, i):
        if self._num_ef_look_up_objects is None:
            # self._ef_lookup_objects is the object, not an array of objects
            return self._ef_lookup_objects
        else:
            return self._ef_lookup_objects[i]

    def _output_species_set(self, i):
        if self._num_ef_look_up_objects is None:
            # self._ef_lookup_objects is the object, not an array of objects
            return self._output_species
        else:
            return self._output_species[i]

    def _set_output_species(self):
        def _one_set(look_up_object):
            s = {}
            for k in ['flaming', 'smoldering', 'residual']:
                if self._species_whitelist:
                    s[k] = self._species_whitelist.intersection(look_up_object.species(k))
                else:
                    s[k] = look_up_object.species(k)
            return s

        if self._num_ef_look_up_objects is None:
            self._output_species = _one_set(self._ef_lookup_objects)
            self._species_by_phase = self._output_species
        else:
            self._output_species = [_one_set(efl) for efl in self._ef_lookup_objects]
            self._species_by_phase = {
                k: reduce(lambda a, b: a.union(b), [os[k] for os in self._output_species])
                    for k in ['flaming', 'smoldering', 'residual']
            }

    ##
    ## Data Validation
    ##

    CATEGORIES_TO_SKIP = {
        'debug',
        'summary'
    }
    VALID_PHASES = {
        'flaming',
        'smoldering',
        'residual'
    }
    def _prune_and_validate(self, consumption_dict):
        """Removes unecessary fields from the consume output dict, and checks
        that what's required is there and valid.

        This method also sets self._num_fuelbeds

        TODO:
         - break this method up into smaller ones
        """
        if not hasattr(consumption_dict, 'items') or 0 == len(list(consumption_dict.items())):
            raise InvalidConsumptionDataError(
                self.ERROR_MESSAGES['INVALID_INPUT_TOP_LEVEL'])

        for category, c_dict in list(consumption_dict.items()):
            if category in self.CATEGORIES_TO_SKIP:
                logging.debug('Ignoring category %s', category)
                consumption_dict.pop(category)
                continue

            if not hasattr(c_dict, 'items') or 0 == len(list(c_dict.items())):
                if self._silent_fail:
                    logging.info('Skipping invalid category %s', category)
                    consumption_dict.pop(category)
                    continue
                else:
                    raise InvalidConsumptionDataError(
                        self.ERROR_MESSAGES['INVALID_INPUT_CATEGORY'] % (category))

            for sub_category, sc_dict in list(c_dict.items()):
                if not hasattr(sc_dict, 'items') or 0 == len(list(sc_dict.items())):
                    if self._silent_fail:
                        logging.info('Skipping invalid sub-category %s', sub_category)
                        c_dict.pop(sub_category)
                        continue
                    else:
                        raise InvalidConsumptionDataError(
                            self.ERROR_MESSAGES['INVALID_INPUT_SUB_CATEGORY'] % (
                            category, sub_category))

                for phase, p_array in list(sc_dict.items()):
                    if phase not in self.VALID_PHASES:
                        logging.debug('Ignoring phase %s', phase)
                        sc_dict.pop(phase)
                        continue

                    p_array_len = None
                    try:
                        # TODO: make sure it's a list or numpy array, not just
                        # that it can be caste to an list (since, for example,
                        # a dict can be caste to an array)
                        p_array_len = len(list(p_array))
                    except:
                        # p_array must not be a list or list-compatible
                        pass
                    self._num_fuelbeds = self._num_fuelbeds or p_array_len
                    if not p_array_len or p_array_len != self._num_fuelbeds:
                        if self._silent_fail:
                            logging.info('Ignoring sub-category %s', phase)
                            sc_dict.pop(phase)
                            continue
                        else:
                            raise InvalidConsumptionDataError(
                                self.ERROR_MESSAGES['INVALID_INPUT_DATA_LENGTH_MISMATCH'] % (
                                category, sub_category, phase))

    ##
    ## Data Initialization
    ##

    def _initialize_emissions_inner_dict(self, include_total=False):
        """Initializes each combustion phase's species-specific emissions
        arrays to 0.0's so that, even if the ef-lookup object has different
        sets of chemical species for the various fuelbeds, each emissions
        array will be the same length).
        """
        d = {
            k: dict([(e, [0.0] * self._num_fuelbeds) for e in self._species_by_phase[k]])
                for k in ['flaming', 'smoldering', 'residual']
        }
        if include_total:
            all_species = reduce(lambda a, b: a.union(b),
                list(self._species_by_phase.values()))
            d['total'] = dict([(e, [0.0] * self._num_fuelbeds)
                for e in all_species])
        return d
