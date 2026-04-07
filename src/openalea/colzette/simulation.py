import pandas as pd

from openalea.colzette.light import light_interception
from openalea.colzette.scene import sowing_map, get_domain, create_scene_one_species, create_mixture_scene
from openalea.colzette.geometry import (RapeseedVisitor, FababeanVisitor,
                                        phenotype_fababean, phenotype_rapeseed)
from openalea.colzette.population import generate_population

def run_static_simulation(das,
                          PlantAge,
                          RG_daily,
                          TLA,
                          option_plants,
                          density,
                          dict_params,
                          type_simul="monocrop_aviso",
                          species='Rapeseed'):

    dict_params = dict_params[species]

    if option_plants == "single":
        sowing_pattern = pd.DataFrame({'x': [0.0], 'y': [0.0]})
    else:
        sowing_pattern = sowing_map(1.0, 1.0, density, type_simul)
    nplants = len(sowing_pattern)

    if species == 'Rapeseed':
        visitor = RapeseedVisitor
        phenotype = phenotype_rapeseed
    else:
        visitor = FababeanVisitor
        phenotype = phenotype_fababean

    if TLA == 0.0:
        vec_Eabs = [0] * nplants
        final_scene = None
        caribu_scene = None
    else:
        domain = get_domain(density, nplants)
        list_of_MTGs, list_of_positions = generate_population(sowing_pattern, dict_params, TLA,
                                                              PlantAge, phenotype, species= species)

        final_scene, shapes_indexer = create_mixture_scene(list_of_MTGs, list_of_positions, sowing_pattern)

        caribu_scene, vec_Eabs = light_interception(final_scene, shapes_indexer, list_of_MTGs, RG_daily, domain)

    vec_das = [das] * nplants
    vec_TT = [PlantAge] * nplants
    sub_dat = pd.DataFrame({'DAS': vec_das,
                            'TT': vec_TT,
                            'Plant': range(0, nplants),
                            'Eabs': vec_Eabs})
    return (final_scene, caribu_scene, sub_dat)