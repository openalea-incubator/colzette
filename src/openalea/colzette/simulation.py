import pandas as pd

from openalea.colzette.light import light_interception
from openalea.colzette.scene import sowing_map_monocrop, sowing_map_intercrop, get_domain, create_scene
from openalea.colzette.geometry import phenotype_fababean, phenotype_rapeseed, phenotype_camelina, phenotype_lentil
from openalea.colzette.population import generate_population, generate_mixture_population

def run_static_simulation(das,
                          PlantAge,
                          RG_daily,
                          TLA,
                          option_plants,
                          density,
                          dict_params,
                          type_simul="monocrop_aviso",
                          species='Rapeseed', ustride=9, vstride=2, light_direction = (0, 0, -1)):

    dict_params = dict_params[species]

    if option_plants == "single":
        sowing_pattern = pd.DataFrame({'x': [0.0], 'y': [0.0], 'species': [species]})
    else:
        sowing_pattern = sowing_map_monocrop(1.0, 1.0, density, species)
    nplants = len(sowing_pattern)

    if species == 'Rapeseed':
        phenotype = phenotype_rapeseed
    elif species == 'Fababean':
        phenotype = phenotype_fababean
    elif species == 'Camelina':
        phenotype = phenotype_camelina
    elif species == 'Lentil':
        phenotype = phenotype_lentil

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

        final_scene, shapes_indexer = create_scene(list_of_MTGs, list_of_positions, sowing_pattern, ustride=ustride, vstride=vstride)

        caribu_scene, vec_Eabs, raw, agg = light_interception(final_scene, shapes_indexer, list_of_MTGs, RG_daily, domain, light_direction=light_direction)

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
                                   TLA_brassica,
                                   TLA_legume,
                                   PlantAge_brassica,
                                   PlantAge_legume,
                                   species_brassica = 'Rapeseed',
                                   species_legume = 'Fababean',
                                   sowing_option = 'rows',
                                   Type_simul="intercrop_aviso_RRF", ustride=9, vstride=2, light_direction = (0, 0, -1)):

    dict_params_brassica = dict_params[species_brassica]
    dict_params_legume = dict_params[species_legume]

    sowing_pattern = sowing_map_intercrop(1.0,
                                1.0,
                                density,
                                species_brassica,
                                species_legume,
                                sowing_option)
    nplants = len(sowing_pattern)
    if TLA_brassica == 0.0 and TLA_legume == 0.0:
        vec_Eabs = [0] * nplants
        final_scene = None
        caribu_scene = None
        raw = None
        agg = None
    else:
        domain = get_domain(density, nplants)

        list_of_MTGs, list_of_positions = generate_mixture_population(sowing_pattern,
                                                                          dict_params_brassica,
                                                                          dict_params_legume,
                                                                          TLA_brassica,
                                                                          TLA_legume,
                                                                          PlantAge_brassica,
                                                                          PlantAge_legume)

        final_scene, shapes_indexer = create_scene(list_of_MTGs, list_of_positions, sowing_pattern, ustride=ustride, vstride=vstride)

        caribu_scene, vec_Eabs, raw, agg = light_interception(final_scene, shapes_indexer, list_of_MTGs, RG_daily, domain, light_direction = light_direction)

    vec_das = [das] * nplants
    vec_TT_brassica = [PlantAge_brassica] * nplants
    vec_TT_legume = [PlantAge_legume] * nplants
    sub_dat = pd.DataFrame({'DAS': vec_das,
                            'TT_brassica': vec_TT_brassica,
                            'TT_legume': vec_TT_legume,
                            'Plant': range(0, nplants),
                            'Eabs': vec_Eabs})
    return (final_scene, caribu_scene, sub_dat, raw, agg)