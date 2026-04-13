
from openalea.colzette.geometry import (
    phenotype_fababean,
    phenotype_rapeseed,
    vegetative)

def generate_population(sowing_pattern,
                        dict_params,
                        TLA,
                        PlantAge,
                        phenotype,
                        species='Rapeseed'):
    list_of_MTGs = []
    list_of_positions = []
    nplants = len(sowing_pattern)
    for id in range(0, nplants):
        xi = sowing_pattern['x'][id] * 100
        yi = sowing_pattern['y'][id] * 100
        gi = vegetative(DJ=PlantAge, dict_params=dict_params, coord=[(xi, yi, 0)], species=species)
        phenotype(gi, TLA, dict_params)

        list_of_MTGs.append(gi.copy())
        list_of_positions.append((xi, yi, 0))
    return list_of_MTGs, list_of_positions

def generate_mixture_population(sowing_pattern,
                                dict_params_rape,
                                dict_params_faba,
                                TLA_rape,
                                TLA_faba,
                                PlantAge_rape,
                                PlantAge_faba):
    list_of_MTGs = []
    list_of_positions = []
    nplants = len(sowing_pattern)
    for id in range(0, nplants):
        # print(id)
        xi = sowing_pattern['x'][id] * 100
        yi = sowing_pattern['y'][id] * 100
        if sowing_pattern['species'][id] == "Fababean":
            gi = vegetative(DJ=PlantAge_faba,
                            dict_params=dict_params_faba,
                            coord=[(xi, yi, 0)], species="Fababean")
            phenotype_fababean(gi,
                               total_surface=TLA_faba,
                               dict_params_faba=dict_params_faba)
        else:
            gi = vegetative(DJ=PlantAge_rape,
                            dict_params=dict_params_rape,
                            coord=[(xi, yi, 0)], species="Rapeseed")
            phenotype_rapeseed(gi,
                               total_surface=TLA_rape,
                               dict_params_rape=dict_params_rape)

        list_of_MTGs.append(gi.copy())
        list_of_positions.append((xi, yi, 0))
    return list_of_MTGs, list_of_positions
