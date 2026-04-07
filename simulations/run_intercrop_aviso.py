
import time
from pathlib import Path # deal with paths in python 3

import pandas

from openalea.colzette.colzette import compute_thermal_time, df_to_dict
from openalea.colzette.population import generate_mixture_population
from openalea.colzette.light import light_interception
from openalea.colzette.scene import create_mixture_scene, sowing_map, get_domain

root_project_dir = Path('.').absolute().parent


start_time = time.time()
data_dir = root_project_dir / 'data'
simul_dir = root_project_dir / 'simulations'
res_dir = root_project_dir / 'results'

# Define identifiers for simulation
Type_simul = "intercrop_aviso_RRF" # type of Total Leaf Area (TLA) curves : monocrop_aviso, monocrop_vigo, monocrop_faba, intercrop_aviso_RRF, intercrop_faba_aviso_RRF, intercrop_vigo, intercrop_faba_vigo
out_dir1 = res_dir / Type_simul
out_dir1.mkdir(exist_ok=True)
out_dir2 = out_dir1 / "Plots"
out_dir2.mkdir(exist_ok=True)

if Type_simul == "intercrop_aviso_RRF":
    Type_rape = "intercrop_aviso_RRF"
    Type_faba = "intercrop_faba_aviso_RRF"
elif Type_simul == "intercrop_vigo_RRF":
    Type_rape = "intercrop_vigo"
    Type_faba = "intercrop_faba_vigo"
else:
    print("Type_simul should be intercrop_aviso_RRF (default) or intercrop_vigo_RRF, other options are not supported")
    Type_rape = "intercrop_aviso_RRF"
    Type_simul = "intercrop_faba_aviso_RRF"

# Read climate file for the chosen simulation site
meteo_fn = data_dir / 'climate' / 'IDEEV_2023_INRAE_STATION_91272001.csv'
clim= pandas.read_csv(meteo_fn,sep=";",skiprows=11)
clim['TM'] = (clim['TN'] + clim['TX'])/2
sowing_rapeseed = "14/09/2023"
sowing_fababean = "20/09/2023"
Tb_rapeseed = 0
Tb_fababean = 0
idx_rapeseed = clim.index[
    (clim["AN"] == 2023) &
    (clim["MOIS"] == 9) &
    (clim["JOUR"] == 14)][0] # rapeseed sowing date 14/09/2023
idx_fababean = clim.index[
    (clim["AN"] == 2023) &
    (clim["MOIS"] == 9) &
    (clim["JOUR"] == 20)][0] # rapeseed sowing date 14/09/2023
clim2 = clim.iloc[idx_rapeseed:]
clim2['TT_rape'] = compute_thermal_time(vec_temp=clim2['TM'], idx_begin=0, Tb=Tb_rapeseed)
clim2['TT_faba'] = compute_thermal_time(vec_temp=clim2['TM'], idx_begin=idx_fababean-1, Tb=Tb_fababean)

# Read Total Leaf Area data (TLA) for the chosen simulation site
TLA_fn = data_dir / 'input_leaf_surface' / 'set_TLA_IDEEV.csv'
TLA_all = pandas.read_csv(TLA_fn,sep="\t")
TLA_indices_keep_rape = TLA_all[TLA_all['Type']==Type_rape].index
vec_TLA_rape = TLA_all['sim'].values[TLA_indices_keep_rape]
TLA_indices_keep_faba = TLA_all[TLA_all['Type']==Type_faba].index
vec_TLA_faba = TLA_all['sim'].values[TLA_indices_keep_faba]

# Read parameters based on option (default or specific to an experimental treatment)
# i.e. Type_simul identifier
#option_parameters = "Default"
option_parameters = Type_simul
dict_params = df_to_dict(data_dir,option_parameters,Type_simul,"")
#dict_params['Rapeseed']['phyllot']=137.5
#dict_params['fababean']['phyllot']=163.5
density = 48.0
iday = 84

def run_static_mixture(iday,
                       clim2,
                       density,
                       dict_params,
                       vec_TLA_rape,
                       vec_TLA_faba):
    
    PlantAge_rape = clim2.iloc[iday]['TT_rape']
    PlantAge_faba = clim2.iloc[iday]['TT_faba']
    RG_daily = clim2.iloc[iday]['PAR']
    dict_params_rape = dict_params['Rapeseed']
    dict_params_faba = dict_params['fababean']

    sowing_pattern = sowing_map(1.0,
                            1.0,
                            density,
                            Type_simul)
    nplants = len(sowing_pattern)
    if vec_TLA_rape[iday] == 0.0 and vec_TLA_faba[iday] == 0.0:
        vec_Eabs = [0]*nplants
        final_scene = None
    else:
        domain = get_domain(density, nplants)

        list_of_MTGs, list_of_positions = generate_mixture_population(sowing_pattern,
                                                                    dict_params_rape,
                                                                    dict_params_faba,
                                                                    vec_TLA_rape,
                                                                    vec_TLA_faba,
                                                                    PlantAge_rape,
                                                                    PlantAge_faba,
                                                                    iday)
        final_scene, shapes_indexer = create_mixture_scene(list_of_MTGs,
                                                        list_of_positions,
                                                        sowing_pattern)
        cs, vec_Eabs = light_interception(final_scene,
                                        shapes_indexer,
                                        list_of_MTGs,
                                        RG_daily,
                                        domain)
    vec_das = [iday] * nplants
    vec_TT_rape = [PlantAge_rape] * nplants
    vec_TT_faba = [PlantAge_faba] * nplants
    sub_dat = pandas.DataFrame({'DAS':vec_das,
                                'TT_rape':vec_TT_rape,
                                'TT_faba' : vec_TT_faba,
                                'Plant': range(0,nplants),
                                'Eabs':vec_Eabs})
    return(final_scene, sub_dat)

def run_dynamic_mixture(clim2,
                        density,
                        dict_params,
                        vec_TLA_rape,
                        vec_TLA_faba):
    dfs = []
    for iday in range(0,len(clim2)):
        print(iday)
        scene, sub_dat = run_static_mixture(iday,
                                     clim2,
                                     density,
                                     dict_params,
                                     vec_TLA_rape,
                                     vec_TLA_faba)
        dfs.append(sub_dat)
        if iday == 84:
            scene2 = scene
        
    df = pandas.concat(dfs,ignore_index=True)
    return(df, scene2)

#res = run_static_mixture(84, clim2, 33.0,dict_params,vec_TLA_rape,vec_TLA_faba)
res, scene = run_dynamic_mixture(clim2, 33.0,dict_params,vec_TLA_rape,vec_TLA_faba)
res.to_csv(out_dir1 / f'res_Eabs_{Type_simul}.csv')