
from openalea.colzette.geometry import (
    vegetative_fababean, phenotype_fababean,
    vegetative_rapeseed, phenotype_rapeseed,
    vegetative)

def generate_rapeseed_population(sowing_pattern, dict_params_rape, vec_TLA_rape, PlantAge_rape, iday):
    list_of_MTGs = []
    list_of_positions = []
    nplants = len(sowing_pattern)
    for id in range(0, nplants):
        # print(id)
        xi = sowing_pattern['x'][id] * 100
        yi = sowing_pattern['y'][id] * 100
        gi = vegetative_rapeseed(DJ=PlantAge_rape,
                                 dict_params=dict_params_rape,
                                 coord=[(xi, yi, 0)])
        phenotype_rapeseed(gi,
                           total_surface=vec_TLA_rape[iday],
                           dict_params_rape=dict_params_rape)

        list_of_MTGs.append(gi.copy())
        list_of_positions.append((xi, yi, 0))
    return list_of_MTGs, list_of_positions

def generate_fababean_population(sowing_pattern,
                                 dict_params_faba,
                                 vec_TLA_faba,
                                 PlantAge_faba,
                                 iday):
    list_of_MTGs = []
    list_of_positions = []
    nplants = len(sowing_pattern)
    for id in range(0, nplants):
        # print(id)
        xi = sowing_pattern['x'][id] * 100
        yi = sowing_pattern['y'][id] * 100
        gi = vegetative_fababean(DJ=PlantAge_faba,
                                 dict_params=dict_params_faba,
                                 coord=[(xi, yi, 0)])
        phenotype_fababean(gi,
                           total_surface=vec_TLA_faba[iday],
                           dict_params_faba=dict_params_faba)

        list_of_MTGs.append(gi.copy())
        list_of_positions.append((xi, yi, 0))
    return list_of_MTGs, list_of_positions

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
        phenotype(gi, total_surface=TLA, dict_params=dict_params)

        list_of_MTGs.append(gi.copy())
        list_of_positions.append((xi, yi, 0))
    return list_of_MTGs, list_of_positions

def generate_mixture_population(sowing_pattern,
                                dict_params_rape,
                                dict_params_faba,
                                vec_TLA_rape,
                                vec_TLA_faba,
                                PlantAge_rape,
                                PlantAge_faba,
                                iday):
    list_of_MTGs = []
    list_of_positions = []
    nplants = len(sowing_pattern)
    for id in range(0, nplants):
        # print(id)
        xi = sowing_pattern['x'][id] * 100
        yi = sowing_pattern['y'][id] * 100
        if sowing_pattern['species'][id] == "Fababean":
            gi = vegetative_fababean(DJ=PlantAge_faba,
                                     dict_params_faba=dict_params_faba,
                                     coord=[(xi, yi, 0)])
            phenotype_fababean(gi,
                               total_surface=vec_TLA_faba[iday],
                               dict_params_faba=dict_params_faba)
        else:
            gi = vegetative_rapeseed(DJ=PlantAge_rape,
                                     dict_params_rape=dict_params_rape,
                                     coord=[(xi, yi, 0)])
            phenotype_rapeseed(gi,
                               total_surface=vec_TLA_rape[iday],
                               dict_params_rape=dict_params_rape)

        list_of_MTGs.append(gi.copy())
        list_of_positions.append((xi, yi, 0))
    return list_of_MTGs, list_of_positions
