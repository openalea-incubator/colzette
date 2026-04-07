import pandas as pd

from openalea.colzette.light import light_interception
from openalea.colzette.scene import sowing_map, get_domain, create_scene
from openalea.colzette.geometry import phenotype_fababean, phenotype_rapeseed
from openalea.colzette.population import generate_population, generate_mixture_population

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
        sowing_pattern = pd.DataFrame({'x': [0.0], 'y': [0.0], 'species': [species]})
    else:
        sowing_pattern = sowing_map(1.0, 1.0, density, type_simul)
    nplants = len(sowing_pattern)

    if species == 'Rapeseed':
        phenotype = phenotype_rapeseed
    else:
        phenotype = phenotype_fababean

    if TLA == 0.0:
        vec_Eabs = [0] * nplants
        final_scene = None
        caribu_scene = None
        raw = None
        agg = None
    else:
        domain = get_domain(density, nplants)
        list_of_MTGs, list_of_positions = generate_population(sowing_pattern, dict_params, TLA,
                                                              PlantAge, phenotype, species= species)

        final_scene, shapes_indexer = create_scene(list_of_MTGs, list_of_positions, sowing_pattern)

        caribu_scene, vec_Eabs, raw, agg = light_interception(final_scene, shapes_indexer, list_of_MTGs, RG_daily, domain)

    vec_das = [das] * nplants
    vec_TT = [PlantAge] * nplants
    sub_dat = pd.DataFrame({'DAS': vec_das,
                            'TT': vec_TT,
                            'Plant': range(0, nplants),
                            'Eabs': vec_Eabs})
    return (final_scene, caribu_scene, sub_dat, raw, agg)


def run_static_mixture_simulation(das,
                                   RG_daily,
                                   density,
                                   dict_params,
                                   TLA_rape,
                                   TLA_faba,
                                   PlantAge_rape,
                                   PlantAge_faba,
                                   Type_simul="intercrop_aviso_RRF"):

    dict_params_rape = dict_params['Rapeseed']
    dict_params_faba = dict_params['Fababean']

    sowing_pattern = sowing_map(1.0,
                                1.0,
                                density,
                                Type_simul)
    nplants = len(sowing_pattern)
    if TLA_rape == 0.0 and TLA_faba == 0.0:
        vec_Eabs = [0] * nplants
        final_scene = None
        caribu_scene = None
        raw = None
        agg = None
    else:
        domain = get_domain(density, nplants)

        list_of_MTGs, list_of_positions = generate_mixture_population(sowing_pattern,
                                                                          dict_params_rape,
                                                                          dict_params_faba,
                                                                          TLA_rape,
                                                                          TLA_faba,
                                                                          PlantAge_rape,
                                                                          PlantAge_faba)

        final_scene, shapes_indexer = create_scene(list_of_MTGs, list_of_positions, sowing_pattern)

        caribu_scene, vec_Eabs, raw, agg = light_interception(final_scene, shapes_indexer, list_of_MTGs, RG_daily, domain)

    vec_das = [das] * nplants
    vec_TT_rape = [PlantAge_rape] * nplants
    vec_TT_faba = [PlantAge_faba] * nplants
    sub_dat = pd.DataFrame({'DAS': vec_das,
                            'TT_rape': vec_TT_rape,
                            'TT_faba': vec_TT_faba,
                            'Plant': range(0, nplants),
                            'Eabs': vec_Eabs})
    return (final_scene, caribu_scene, sub_dat, raw, agg)