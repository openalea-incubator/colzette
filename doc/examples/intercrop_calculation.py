#!/usr/bin/env python
# coding: utf-8

# # Basic usage of colzette

# In[1]:


import sys
import pandas

from pathlib import Path

from openalea.colzette.colzette import compute_thermal_time, df_to_dict
from openalea.colzette.simulation import run_static_mixture_simulation


# In[2]:


data_dir = Path('data')


# ## Define identifiers for simulation

# In[3]:


Type_simul = 'intercrop_vigo' # 'intercrop_aviso_RRF', 'intercrop_vigo'
if Type_simul == "intercrop_aviso_RRF":
    Type_rape = "intercrop_aviso_RRF"
    Type_faba = "intercrop_faba_aviso_RRF"
else:
    Type_rape = "intercrop_vigo"
    Type_faba = "intercrop_faba_vigo"


# ## Read climate file for the chosen simulation site

# In[4]:


meteo_fn = data_dir / 'climate' / 'IDEEV_2023_INRAE_STATION_91272001.csv'
clim= pandas.read_csv(meteo_fn,sep=";",skiprows=11)
clim['TM'] = (clim['TN'] + clim['TX'])/2

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


# ## Read Total Leaf Area data (TLA) for the chosen simulation site

# In[5]:


TLA_fn = data_dir / 'input_leaf_surface' / 'set_TLA_IDEEV.csv'
TLA_all = pandas.read_csv(TLA_fn,sep="\t")
TLA_indices_keep_rape = TLA_all[TLA_all['Type']==Type_rape].index
vec_TLA_rape = TLA_all['sim'].values[TLA_indices_keep_rape]
TLA_indices_keep_faba = TLA_all[TLA_all['Type']==Type_faba].index
vec_TLA_faba = TLA_all['sim'].values[TLA_indices_keep_faba]


# ## Read parameters based on option (default or specific to an experimental treatment)

# In[6]:


dict_params = df_to_dict(data_dir,Type_simul,Type_simul,"")
density=48.0
option_plants = 'plot' # 'plot' or 'single' i.e. crop or one plant


# ## run simulation over the whole clim data

# In[7]:


dfs = []
list_scene = []
list_cs = []
list_raw = [] 
list_agg = []

for iday in range(0,len(clim2)):

    # just to display running activity
    sys.stdout.write('\r')
    sys.stdout.write(f'{iday/(len(clim2)-1)*100:.0f}' + '%')  # pad to overwrite leftovers
    sys.stdout.flush()

    PlantAge_rape = clim2.iloc[iday]['TT_rape']
    PlantAge_faba = clim2.iloc[iday]['TT_faba']
    RG_daily = clim2.iloc[iday]['PAR']
    TLA_rape = vec_TLA_rape[iday]
    TLA_faba = vec_TLA_faba[iday]
    scene, caribu_scene, sub_dat, raw, agg = run_static_mixture_simulation(iday,
                                  RG_daily,
                                   density,
                                   dict_params,
                                   TLA_rape,
                                   TLA_faba,
                                   PlantAge_rape,
                                   PlantAge_faba,
                                   Type_simul=Type_simul)
    dfs.append(sub_dat)
    list_scene.append(scene)
    list_cs.append(caribu_scene)
    list_raw.append(raw)
    list_agg.append(agg)

res = pandas.concat(dfs,ignore_index=True)


# In[8]:


res.to_csv(f'res_Eabs_{Type_simul}.csv')


# ## Display 3D
# 
# `openalea.widgets` need to be installed

# In[9]:


from openalea.widgets.plantgl import PlantGL


# In[12]:


das=50 # day after sowing
# raw, agg = list_cs[das].run(infinite=True, simplify=True, direct=True)
# scene, values = list_cs[das].plot(agg['Eabs'], display = False)

scene, values = list_cs[das].plot(list_agg[das]['Eabs'], display = False)


# In[13]:


PlantGL(scene, group_by_color=False, side='double')


# In[ ]:




