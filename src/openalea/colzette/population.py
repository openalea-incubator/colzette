
from openalea.colzette.geometry import (
    phenotype_fababean,
    phenotype_rapeseed,
    phenotype_camelina,
    phenotype_lentil,
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
                                dict_params_brassica,
                                dict_params_legume,
                                TLA_brassica,
                                TLA_legume,
                                PlantAge_brassica,
                                PlantAge_legume):
    list_of_MTGs = []
    list_of_positions = []
    nplants = len(sowing_pattern)
    for id in range(0, nplants):
        # print(id)
        xi = sowing_pattern['x'][id] * 100
        yi = sowing_pattern['y'][id] * 100
        if sowing_pattern['species'][id] == "Fababean":
            gi = vegetative(DJ=PlantAge_legume,
                            dict_params=dict_params_legume,
                            coord=[(xi, yi, 0)], species="Fababean")
            phenotype_fababean(gi,
                               total_surface=TLA_legume,
                               dict_params_faba=dict_params_legume)
        elif sowing_pattern['species'][id] == "Lentil":
            gi = vegetative(DJ=PlantAge_legume,
                            dict_params=dict_params_legume,
                            coord=[(xi, yi, 0)], species="Lentil")
            phenotype_lentil(gi,
                               total_surface=TLA_legume,
                               dict_params_lent=dict_params_legume)
        elif sowing_pattern['species'][id] == "Rapeseed":
            gi = vegetative(DJ=PlantAge_brassica,
                            dict_params=dict_params_brassica,
                            coord=[(xi, yi, 0)], species="Rapeseed")
            phenotype_rapeseed(gi,
                               total_surface=TLA_brassica,
                               dict_params_rape=dict_params_brassica)
        elif sowing_pattern['species'][id] == "Camelina":
            gi = vegetative(DJ=PlantAge_brassica,
                            dict_params=dict_params_brassica,
                            coord=[(xi, yi, 0)], species="Camelina")
            phenotype_camelina(gi,
                               total_surface=TLA_brassica,
                               dict_params_came=dict_params_brassica)

        list_of_MTGs.append(gi.copy())
        list_of_positions.append((xi, yi, 0))
    return list_of_MTGs, list_of_positions
