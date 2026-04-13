
import time
from pathlib import Path # deal with paths in python 3

import pandas

from openalea.colzette.colzette import compute_thermal_time, df_to_dict
from openalea.colzette.population import generate_population
from openalea.colzette.geometry import phenotype_rapeseed, RapeseedVisitor
from openalea.colzette.light import light_interception
from openalea.colzette.scene import create_scene_one_species, sowing_map, get_domain

root_project_dir = Path('.').absolute().parent


start_time = time.time()
data_dir = root_project_dir / 'data'
simul_dir = root_project_dir / 'simulations'
res_dir = root_project_dir / 'results'

# Define identifiers for simulation
Type_simul = "monocrop_vigo" # type of Total Leaf Area (TLA) curves : monocrop_aviso, monocrop_vigo, monocrop_faba, intercrop_aviso_RRF, intercrop_faba_aviso_RRF, intercrop_vigo, intercrop_faba_vigo
out_dir1 = res_dir / Type_simul
out_dir1.mkdir(exist_ok=True)
out_dir2 = out_dir1 / "Plots"
out_dir2.mkdir(exist_ok=True)

# Read climate file for the chosen simulation site
meteo_fn = data_dir / 'climate' / 'IDEEV_2023_INRAE_STATION_91272001.csv'
clim= pandas.read_csv(meteo_fn,sep=";",skiprows=11)
clim['TM'] = (clim['TN'] + clim['TX'])/2
sowing_rapeseed = "14/09/2023"
Tb_rapeseed = 0
idx_rapeseed = clim.index[
    (clim["AN"] == 2023) &
    (clim["MOIS"] == 9) &
    (clim["JOUR"] == 14)][0] # rapeseed sowing date 14/09/2023
clim2 = clim.iloc[idx_rapeseed:]
clim2['TT_rape'] = compute_thermal_time(vec_temp=clim2['TM'], idx_begin=0, Tb=5)

# Read Total Leaf Area data (TLA) for the chosen simulation site
TLA_fn = data_dir / 'input_leaf_surface' / 'set_TLA_IDEEV.csv'
TLA_all = pandas.read_csv(TLA_fn,sep="\t")
TLA_indices_keep = TLA_all[TLA_all['Type']==Type_simul].index
vec_TLA_rape = TLA_all['sim'].values[TLA_indices_keep]

# Read parameters based on option (default or specific to an experimental treatment)
# i.e. Type_simul identifier
#option_parameters = "Default"
option_parameters = Type_simul
dict_params = df_to_dict(data_dir,option_parameters,Type_simul,"")
#dict_params['Rapeseed']['phyllot']=137.5
density=33.0
iday=84

#setting_PGLViewer(width=1200, height=900,
#                x_center=0., y_center=0., z_center=0.,
#                x_cam=0., y_cam=0., z_cam=200,
#                grid=False,
#                background_color=[94, 76, 64])

def run_static_rapeseed(iday, option_plants, clim2, density, dict_params, vec_TLA_rape):
    PlantAge_rape = clim2.iloc[iday]['TT_rape']
    RG_daily = clim2.iloc[iday]['PAR']
    dict_params_rape = dict_params['Rapeseed']
    

    if option_plants == "single":
        sowing_pattern = pandas.DataFrame({'x':[0.0],
                                'y':[0.0]})
    else:
        sowing_pattern = sowing_map(1.0,
                                    1.0,
                                    density,
                                    Type_simul)
        
    nplants = len(sowing_pattern)
    if vec_TLA_rape[iday] == 0.0:
        vec_Eabs = [0]*nplants
        final_scene = None
    else:
        domain = get_domain(density, nplants)
        list_of_MTGs, list_of_positions = generate_population(sowing_pattern,
                                                                dict_params_rape,
                                                                vec_TLA_rape[iday],
                                                                PlantAge_rape,
                                                                phenotype_rapeseed,
                                                                species='Rapeseed')


        final_scene, shapes_indexer = create_scene_one_species(list_of_MTGs,
                                                        list_of_positions, RapeseedVisitor)


        cs, vec_Eabs, raw, agg = light_interception(final_scene,
                                    shapes_indexer,
                                    list_of_MTGs,
                                    RG_daily,
                                    domain)
    vec_das = [iday] * nplants
    vec_TT_rape = [PlantAge_rape] * nplants
    sub_dat = pandas.DataFrame({'DAS':vec_das,
                                'TT_rape' : vec_TT_rape,
                                'Plant': range(0,nplants),
                                'Eabs':vec_Eabs})    
    return(final_scene, sub_dat)

def run_dynamic_rapeseed(option_plants, clim2, density, dict_params,vec_TLA_rape):
    dfs = []
    for iday in range(11): #range(0,len(clim2)):
        print(iday)
        scene, sub_dat = run_static_rapeseed(iday,
                                      option_plants,
                                      clim2,
                                      density,
                                      dict_params,
                                      vec_TLA_rape)
        dfs.append(sub_dat)
        if iday == 10:
            scene2 = scene

    df = pandas.concat(dfs,ignore_index=True)
    return df, scene2


#res = run_static_rapeseed(84, "single", clim2, 33.0, dict_params, vec_TLA_rape)
#res = run_static_rapeseed(84, "plot", clim2, 33.0, dict_params, vec_TLA_rape)

#res = run_dynamic_rapeseed("single", clim2, 33.0, dict_params,vec_TLA_rape)
res, scene = run_dynamic_rapeseed("plot", clim2, 33.0, dict_params,vec_TLA_rape)
res.to_csv(out_dir1 / f'res_Eabs_{Type_simul}.csv')
