"""
Colzette library
"""

import numpy as np
import pandas as pd

import openalea.plantgl.all as pgl
from openalea.mtg import MTG, fat_mtg
from openalea.plantgl.all import Vector3, Color3, Viewer

def df_to_dict(data_dir,option_parameters,Type_simul,par_DOE):
    if option_parameters == "Default":
        params_fn_rape = data_dir / 'parameters' / 'global_params_rapeseed.csv'
        params_fn_faba = data_dir / 'parameters' / 'global_params_fababean.csv'
        df_par_rape = pd.read_csv(params_fn_rape,sep='\t')
        df_par_faba = pd.read_csv(params_fn_faba,sep='\t')

        if Type_simul == "monocrop_aviso" or Type_simul == "monocrop_vigo":
            df_par = df_par_rape
        elif Type_simul == "monocrop_faba":
            df_par = df_par_faba
        else:
            df_par = pd.concat([df_par_rape, df_par_faba])

        df_par = df_par[df_par['Level']=='Default']
        dict_params = {} 
        for sp in df_par['Species'].unique():
            dict_params_sp = {}
            df_par2 = df_par[df_par['Species']==sp]
            for par in df_par2['Parameter'].unique():
                dict_params_sp[par] = df_par2.loc[df_par2['Parameter']==par,'Value'].iloc[0]
            dict_params[sp] = dict_params_sp
    elif option_parameters == "DOE_metamodel":
        if Type_simul == "metamodel_rapeseed":
            vec_species=['Rapeseed']
        elif Type_simul == "metamodel_fababean":
            vec_species = ['fababean']
        else:
            vec_species = ['Rapeseed','fababean']
        dict_params = {}
        for sp in vec_species:
            # here in mixture select columns for species parameters, df_par = ...
            df_par = par_DOE
            # loop for sp in vec_species
            dict_params_id = {}
            for id in df_par.index:
                df_par2 = df_par.iloc[id]
                dict_params_sp = {}
                for par in df_par2.keys():
                    dict_params_sp[par] = df_par2[par]
                    # here also set default parameter values
                dict_params_id[id] = dict_params_sp
            dict_params[sp] = dict_params_id
    else:
        params_fn_rape = data_dir / 'parameters' / 'type_params_rapeseed.csv'
        params_fn_faba = data_dir / 'parameters' / 'type_params_fababean.csv'
        df_par_rape = pd.read_csv(params_fn_rape,sep='\t')
        df_par_faba = pd.read_csv(params_fn_faba,sep='\t')

        if Type_simul == "monocrop_aviso" or Type_simul == "monocrop_vigo":
            df_par = df_par_rape
            df_par = df_par[df_par['Treatment'] == Type_simul]
        elif Type_simul == "monocrop_faba":
            df_par = df_par_faba
            df_par = df_par[df_par['Treatment'] == Type_simul]
        else:
            if Type_simul == "intercrop_aviso_RRF":
                Type_simul2 = "intercrop_faba_aviso_RRF"
            elif Type_simul == "intercrop_aviso_RF":
                Type_simul2 = "intercrop_faba_aviso_RF"
            elif Type_simul == "intercrop_vigo":
                Type_simul2 = "intercrop_faba_vigo"
            df_par_rape = df_par_rape[df_par_rape['Treatment'] == Type_simul]
            df_par_faba = df_par_faba[df_par_faba['Treatment'] == Type_simul2]
            df_par = pd.concat([df_par_rape, df_par_faba])
        
        df_par = df_par[df_par['Level'] == 'Default']

        dict_params = {}
        for sp in df_par['Species'].unique():
            dict_params_sp = {}
            df_par2 = df_par[df_par['Species']==sp]
            for par in df_par2['Parameter'].unique():
                dict_params_sp[par] = df_par2.loc[df_par2['Parameter']==par,'Value'].iloc[0]
            if sp == 'Rapeseed':
                dict_params_sp['phylloc'] = 0.016
            else:
                dict_params_sp['phylloc'] = 0.0128
            dict_params[sp] = dict_params_sp
    return(dict_params)

def compute_thermal_time(vec_temp, idx_begin, Tb):
    vec_temp2 = vec_temp
    vec_temp2[:idx_begin] = 0
    vec_temp2[vec_temp2 < Tb] = 0
    vec_TT = vec_temp2.cumsum()
    return vec_TT

def get_nb_leaflets(rank):
    if rank <= 6:
        nb_leaflets = 2.0
    elif rank == 7:
        nb_leaflets = 3.0
    elif rank >= 10:
        nb_leaflets = 5.0
    elif (rank >= 8 & rank <= 9):
        nb_leaflets = 4.0
    return nb_leaflets

class Plant:
    """ Define a plant as an above and below ground MTG.

    Some usefull functions can be defined as proxies.
    
    """
    def __init__(self, name='', above=None, below=None):
        self.name = name
        self.above = self.init_above_mtg() if above is None else above
        self.below = self.init_below_mtg() if below is None else below


    @staticmethod
    def init_above_mtg():
        """ Simple function to create a simple aerial MTG"""
        g = MTG()
        
        # Add a plant (scale is 1)
        vid = g.add_component(g.root, label='Plant')
        #vid = g.add_component(vid, label='Axis')
        #vid = g.add_component(vid, label='Phytomer')
        
        # Last scale
        vid = g.add_component(vid, label='Internode')
        leaf_id = g.add_child(vid, edge_type='+', label='Leaf')
        #bud_id = g.add_component(vid, edge_type='<', label='Bud')

        #fat_mtg(g)
        return g

    @staticmethod
    def init_below_mtg():
        """ Simple function to create a simple belowground MTG or RootSystem Architecture"""
        g = MTG()
        
        # Add a plant (scale is 1)
        vid = g.add_component(g.root, label='RSA')
        vid = g.add_component(vid, label='Root')
        
        # Last scale
        vid = g.add_component(vid, label='Segment')
    
        fat_mtg(g)
        return g

def update_MTG(g, outputs):
    """
    Update the MTG 
    :param dict outputs: {'param1': { vid1: , vid2, ...}, 'param2': { vid1: , vid2, ...}}
    """
     # add the missing property
    for param in outputs.keys():
        if param not in g.properties():
            g.add_property(param)

        # update the MTG
        g.property(param).update(outputs[param])   

def bell_shaped_dist(total_area=1, nb_phy=15, rmax=.7, skewness=5):
    """ OLD, use generate_normalized_bell_curve_points() instead
    returns the leaf area of individual leaves along a bell shaped model, as a proportion of the total leaf area """

    r = np.linspace(1./nb_phy, 1, nb_phy)
    k = skewness
    relative_surface = np.exp(-k / rmax * ( 2 * (r - rmax)**2 + (r - rmax)**3))
    leaf_area = relative_surface / relative_surface.sum() * total_area
    return leaf_area.tolist()

def setting_PGLViewer(width=1200, height=1200,
                      x_center=0., y_center=0., z_center=0.,
                      x_cam=0., y_cam=0., z_cam=-0.2,
                      grid=True,
                      background_color=[255, 255, 255]):
    """
    This function sets the center of the graph and the relative position of the camera for displaying a scene in
    PGL.
    :param width: width of the window (pixels)
    :param height: height of the window (pixels)
    :param x_center: x-coordinate of the center at which the camera looks
    :param y_center: y-coordinate of the center at which the camera looks
    :param z_center: z-coordinate of the center at which the camera looks
    :param x_cam: x-coordinate of the camera position
    :param y_cam: y-coordinate of the camera position
    :param z_cam: z-coordinate of the camera position
    :param grid: if True, all grids will be displayed
    :param background_color: a RGB vector corresponding to the background color of the graph
    :return:
    """

    # We define the coordinates of the point cam_target that will be the center of the graph:
    cam_target = pgl.Vector3(x_center, y_center, z_center)
    # We define the coordinates of the point cam_pos that represents the position of the camera:
    cam_pos = pgl.Vector3(x_cam, y_cam, z_cam)
    # We position the camera in the scene relatively to the center of the scene:
    pgl.Viewer.camera.lookAt(cam_pos, cam_target)
    # We define the dimensions of the graph:
    pgl.Viewer.frameGL.setSize(width, height)
    # We define the background of the scene:
    pgl.Viewer.frameGL.setBgColor(background_color[0], background_color[1], background_color[2])
    # We define whether grids are displayed or not:
    pgl.Viewer.grids.set(grid, grid, grid, grid)

    return


