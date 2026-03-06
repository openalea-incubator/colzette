"""
Colzette library
"""

from openalea.mtg import *
from openalea.mtg.turtle import *
from openalea.plantgl import all as pgl
from openalea.plantgl.all import *
from openalea.plantgl.all import Vector3, Color3, Scaled, Viewer
from numpy import *
import numpy as np
import openalea.plantgl.all as pgl
import pandas as pd
from openalea.mtg import turtle as turt
from openalea.caribu.CaribuScene import CaribuScene

def generate_rapeseed_population(sowing_pattern,dict_params_rape, vec_TLA_rape, PlantAge_rape,iday):
    list_of_MTGs = []
    list_of_positions = []
    nplants=len(sowing_pattern)
    for id in range(0,nplants): 
        print(id)   
        xi = sowing_pattern['x'][id]*100
        yi = sowing_pattern['y'][id]*100
        gi = vegetative_rapeseed(DJ = PlantAge_rape,
                                dict_params_rape=dict_params_rape,
                                coord=[(xi,yi, 0)])
        phenotype_rapeseed(gi,
            total_surface=vec_TLA_rape[iday],
            dict_params_rape=dict_params_rape)
        
        list_of_MTGs.append(gi.copy())
        list_of_positions.append((xi,yi,0))
    return list_of_MTGs, list_of_positions

def generate_fababean_population(sowing_pattern,
                                 dict_params_faba,
                                 vec_TLA_faba,
                                 PlantAge_faba,
                                 iday):
    list_of_MTGs = []
    list_of_positions = []
    nplants=len(sowing_pattern)
    for id in range(0,nplants): 
        print(id)   
        xi = sowing_pattern['x'][id]*100
        yi = sowing_pattern['y'][id]*100
        gi = vegetative_fababean(DJ = PlantAge_faba,
                                dict_params_faba=dict_params_faba,
                                coord=[(xi,yi, 0)])
        phenotype_fababean(gi,
            total_surface=vec_TLA_faba[iday],
            dict_params_faba=dict_params_faba)
        
        list_of_MTGs.append(gi.copy())
        list_of_positions.append((xi,yi,0))
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
    nplants=len(sowing_pattern)
    for id in range(0,nplants): 
        print(id)   
        xi = sowing_pattern['x'][id]*100
        yi = sowing_pattern['y'][id]*100
        if sowing_pattern['species'][id] == "Fababean":
            gi = vegetative_fababean(DJ = PlantAge_faba,
                                    dict_params_faba=dict_params_faba,
                                    coord=[(xi,yi, 0)])
            phenotype_fababean(gi,
                total_surface=vec_TLA_faba[iday],
                dict_params_faba=dict_params_faba)
        else:
            gi = vegetative_rapeseed(DJ = PlantAge_rape,
                                    dict_params_rape=dict_params_rape,
                                    coord=[(xi,yi, 0)])
            phenotype_rapeseed(gi,
                total_surface=vec_TLA_rape[iday],
                dict_params_rape=dict_params_rape)            
        
        list_of_MTGs.append(gi.copy())
        list_of_positions.append((xi,yi,0))
    return list_of_MTGs, list_of_positions

def create_rapeseed_scene(list_of_MTGs, list_of_positions):
    # function 2 to compute final scene and new indices
    # We initialize additional properties of scene_information:
    list_rotation = []
    # We initialize an indexer that will record the correspondance between the initial vid of the MTG and the new,
    # unique indices of the scene:
    shapes_indexer = {}
    # We initialize a unique shape ID for new indexing across all plants in the scene
    unique_shape_id = 1

    # We initialize a turtle in PlantGL:
    turtle = turt.PglTurtle()
    # We initialize the final scene:
    final_scene = pgl.Scene()

    for plant_index in range(0,len(list_of_positions)):
        #print(plant_index)
        # We access the MTG corresponding to the current plant index:
        new_MTG = list_of_MTGs[plant_index]

        # We initialize the indexer for the current plant:
        shapes_indexer[plant_index] = {}

        # We first define the seed of random, depending on the index of the plant:
        np.random.seed(int(2.0 * plant_index))
        # We then modify the angle of the plant, so that leaves are not oriented the same way within the population:
        angle_roll = abs(np.random.normal(180, 180))
        # We record this rotation in the scene information:
        list_rotation.append(angle_roll)

        # We reset the turtle:
        turtle.reset()
        # And we reposition the turtle from there:
        turtle.move(list_of_positions[plant_index])
        turtle.rollR(angle_roll)
        # We create a scene for one plant by moving the turtle along the MTG:
        scene = turt.TurtleFrame(new_MTG,
                                    visitor=RapeseedVisitor,
                                    turtle=turtle, gc=False)

        scene_dict = scene.todict()
        dict_organs = {}

        for old_shape_id in scene_dict.keys():
            shapes = scene_dict[old_shape_id]
            if len(shapes)==1:
                # internode shape
                shape = shapes[0]
                dict_organs[unique_shape_id] = 'Internode'
                shapes_indexer[plant_index][unique_shape_id] = old_shape_id
                shape.id = unique_shape_id
                final_scene += shape
                unique_shape_id += 1
            elif len(shapes)==2:
                # leaf shape with leaf + petiole
                shape1 = shapes[0] # leaf
                dict_organs[unique_shape_id] = 'Leaf'
                shapes_indexer[plant_index][unique_shape_id] = old_shape_id
                shape1.id = unique_shape_id
                final_scene += shape1
                unique_shape_id += 1

                shape2 = shapes[1] # petiole
                dict_organs[unique_shape_id] = 'Petiole'
                shapes_indexer[plant_index][unique_shape_id] = old_shape_id
                shape2.id = unique_shape_id
                final_scene += shape2
                unique_shape_id += 1
    return final_scene, shapes_indexer

def create_mixture_scene(list_of_MTGs, list_of_positions, sowing_pattern):
    list_rotation = []
    shapes_indexer = {}
    unique_shape_id = 1
    turtle = turt.PglTurtle()
    final_scene = pgl.Scene()

    for plant_index in range(0,len(list_of_positions)):
        print(plant_index)
        new_MTG = list_of_MTGs[plant_index]
        shapes_indexer[plant_index] = {}
        np.random.seed(int(2.0 * plant_index))
        angle_roll = abs(np.random.normal(180, 180))
        list_rotation.append(angle_roll)
        turtle.reset()
        turtle.move(list_of_positions[plant_index])
        turtle.rollR(angle_roll)
        if sowing_pattern['species'][plant_index] == "Fababean":
            scene = turt.TurtleFrame(new_MTG,
                                        visitor=FababeanVisitor,
                                        turtle=turtle, gc=False)
            scene_dict = scene.todict()
            dict_organs = {}

            for old_shape_id in scene_dict.keys():
                shapes = scene_dict[old_shape_id]
                shape = shapes[0]
                shapes_indexer[plant_index][unique_shape_id] = old_shape_id
                shape.id = unique_shape_id
                final_scene += shape
                unique_shape_id += 1
        else:
            scene = turt.TurtleFrame(new_MTG,
                                        visitor=RapeseedVisitor,
                                        turtle=turtle, gc=False)
            scene_dict = scene.todict()
            dict_organs = {}

        for old_shape_id in scene_dict.keys():
            shapes = scene_dict[old_shape_id]
            if len(shapes)==1:
                # internode shape
                shape = shapes[0]
                dict_organs[unique_shape_id] = 'Internode'
                shapes_indexer[plant_index][unique_shape_id] = old_shape_id
                shape.id = unique_shape_id
                final_scene += shape
                unique_shape_id += 1
            elif len(shapes)==2:
                # leaf shape with leaf + petiole
                shape1 = shapes[0] # leaf
                dict_organs[unique_shape_id] = 'Leaf'
                shapes_indexer[plant_index][unique_shape_id] = old_shape_id
                shape1.id = unique_shape_id
                final_scene += shape1
                unique_shape_id += 1

                shape2 = shapes[1] # petiole
                dict_organs[unique_shape_id] = 'Petiole'
                shapes_indexer[plant_index][unique_shape_id] = old_shape_id
                shape2.id = unique_shape_id
                final_scene += shape2
                unique_shape_id += 1

    return final_scene, shapes_indexer


def create_fababean_scene(list_of_MTGs, list_of_positions):
    list_rotation = []
    shapes_indexer = {}
    unique_shape_id = 1
    turtle = turt.PglTurtle()
    final_scene = pgl.Scene()

    for plant_index in range(0,len(list_of_positions)):
        new_MTG = list_of_MTGs[plant_index]
        shapes_indexer[plant_index] = {}
        np.random.seed(int(2.0 * plant_index))
        angle_roll = abs(np.random.normal(180, 180))
        list_rotation.append(angle_roll)
        turtle.reset()
        turtle.move(list_of_positions[plant_index])
        turtle.rollR(angle_roll)
        scene = turt.TurtleFrame(new_MTG,
                                    visitor=FababeanVisitor,
                                    turtle=turtle, gc=False)

        scene_dict = scene.todict()
        dict_organs = {}

        for old_shape_id in scene_dict.keys():
            shapes = scene_dict[old_shape_id]
            shape = shapes[0]
            shapes_indexer[plant_index][unique_shape_id] = old_shape_id
            shape.id = unique_shape_id
            final_scene += shape
            unique_shape_id += 1
    return final_scene, shapes_indexer

def light_interception(final_scene, shapes_indexer, list_of_MTGs, RG_daily, domain):
    zenith=[(RG_daily,(0,0,-1))]
    cs = CaribuScene(scene=final_scene, light=zenith, scene_unit='cm', pattern=domain)
    raw, agg = cs.run(infinite=True, simplify=True, direct=True)

    Eabs = agg["Eabs"]
    area = agg["area"]

    vec_Eabs = []
    for plant_index in range(0, len(list_of_MTGs)):
        g = list_of_MTGs[plant_index]
        shapes_plant = shapes_indexer[plant_index]
        g_indices = g.properties()['label']
        g_indices_leaf = [k for k,v in g_indices.items() if v == 'Leaf']
        new_indices_leaf = [k for k,v in shapes_plant.items() if v in g_indices_leaf]

        new_indices_plant = shapes_plant.keys()
        Eabs_plant = {k:v for k,v in Eabs.items() if k in new_indices_plant}
        Eabs_leaves = {k:v for k,v in Eabs_plant.items() if k in new_indices_leaf}
        area_plant = {k:v for k,v in area.items() if k in new_indices_plant}
        area_leaves = {k:v for k,v in area_plant.items() if k in new_indices_leaf}

        intercepted_light = sum([Eabs_leaves[k] * area_leaves[k] for k in Eabs_leaves]) # in J/cm2
        vec_Eabs.append(intercepted_light)
    return cs, vec_Eabs

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
            vec_species = ['Fababean']
        else:
            vec_species = ['Rapeseed','Fababean']
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

def get_domain(density, nb_plantes):
    inter_row=np.sqrt(1/density)
    inter_plant = 1. / inter_row / density
    if nb_plantes == 1:
        nrow=1
    else:
        nrow = np.max([1, int(np.sqrt(nb_plantes))])
    dx = inter_plant * 100
    dy = inter_row * 100
    nx = int(nb_plantes/nrow)
    ny = nrow
    domain = ((0,0),(nx*dx, ny*dy))
    return domain

def sowing_map(
    length,
    width,
    density,
    type = "monocrop_aviso"):

    """
    length, width : plot dimensions (m)
    density : plants per m²
    species1, species2 : names of the two species
    """
    
    species1="Rapeseed"
    species2="Fababean"

    pas = np.sqrt(1 / density)

    xs = np.arange(pas / 2, length, pas)
    ys = np.arange(pas / 2, width, pas)

    data = []

    if type == "monocrop_aviso" or type == "monocrop_vigo":
        for i, y in enumerate(ys):
            for x in xs:
                data.append((x, y, 'Rapeseed'))

    elif type == "monocrop_fababean":
        for i, y in enumerate(ys):
            for x in xs:
                data.append((x, y, 'Fababean'))

    elif type == "intercrop_aviso_RRF" or type == "intercrop_vigo" or type == "intercrop_aviso_RF" :
        for i, y in enumerate(ys):
            species = species1 if i % 2 == 0 else species2
            for x in xs:
                data.append((x, y, species))

    data2 = pd.DataFrame(data, columns=["x", "y", "species"])  
    return data2

# Functions to generate leaf shapes (with leaflets for fababean)
def make_leafshape_rapeseed():
    sc_factor = 3.572567770618656
    pts = lambda x,y,z : Vector4(x/sc_factor,y/sc_factor,z/sc_factor,1.0)
    r1=[pts(0,0,0), pts(7,-0.5,1), pts(3,-3,2), pts(1.5,-5,2.75), pts(-1,0,3)]
    r2=[pts(0,0,0), pts(7,0.5,1), pts(3,3,2), pts(1.5,5,2.75), pts(-1,0,3)]
    m=Point4Matrix([r1,r2])
    leafshape_rapeseed=BezierPatch(m, ustride=9, vstride=2)
    return(leafshape_rapeseed)

#original
def make_leafshape_rapeseed2():
    sc_factor = 3.54673835885395
    pts = lambda x,y,z : Vector4(x/sc_factor,y/sc_factor,z/sc_factor,1.0)
    r1=[pts(0,0,0), pts(5,-0.5,1), pts(5,-3,2), pts(-1,-5,2.75), pts(-1,0,3)]
    r2=[pts(0,0,0), pts(5,0.5,1), pts(5,3,2), pts(-1,5,2.75), pts(-1,0,3)]
    m=Point4Matrix([r1,r2])
    leafshape_rapeseed=BezierPatch(m, ustride=9, vstride=2)
    return(leafshape_rapeseed)

def make_leaflet_shape_fababean():
    sc_factor = 3.173
    pts = lambda x,y,z : Vector4(x/sc_factor,y/sc_factor,z/sc_factor,1.0)
    r1=[pts(0,0,0), pts(0,-1,0.1), pts(0,-2,1), pts(0,-3,2), pts(0,-1,3), pts(0,-1,3.9), pts(0,0,4)]
    r2=[pts(0,0,0), pts(0,1,0.1),  pts(0,2,1),  pts(0,3,2),  pts(0,1,3),  pts(0,1,3.9),  pts(0,0,4)]
    m=Point4Matrix([r1,r2])
    leafletshape_fababean=BezierPatch(m, ustride=9, vstride=2)
    return(leafletshape_fababean)

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


def multi_leaflets(nb_leaflets=5.0,
                   leaf_surface=1.0,
                   coeff_width=0.7, 
                   petiole_leaflet_length1=2.0,
                   petiole_leaflet_length2=2.0,
                   coeff_petiole_d=0.5,
                   stem_d=0.035):
    surface_leaflet = leaf_surface/nb_leaflets # each leaflet has the same surface
    leaflet_length=2*(surface_leaflet/(coeff_width*pi))**(0.5)
    leaflet_width=leaflet_length*coeff_width
    leafscale = Vector3(1, leaflet_width, leaflet_length)
    leafletshape_fababean = make_leaflet_shape_fababean()
    leaflet = Scaled(leafscale,leafletshape_fababean)

    if nb_leaflets < 2:
        nb_petiole = 1
    else:
        nb_petiole = (nb_leaflets)//2
    total_petiole_leaflet = petiole_leaflet_length1 + petiole_leaflet_length2*(nb_petiole-1)
    petiole = Cylinder(radius=stem_d*coeff_petiole_d/2,height=total_petiole_leaflet)
    leaflet_left = AxisRotated(axis=(1,0,0),angle=-radians(60),geometry=leaflet)
    leaflet_right = AxisRotated(axis=(1,0,0),angle=radians(60),geometry=leaflet)
    leaflets = [petiole]
    translate = [0,0,petiole_leaflet_length1]
    count_leaflets = nb_leaflets
    leaflets.append(Translated(translate,leaflet_left))
    leaflets.append(Translated(translate,leaflet_right))
    for i in range(nb_petiole):
        leaflets.append(Translated(translate,leaflet_left))
        leaflets.append(Translated(translate,leaflet_right))
        translate[2] += petiole_leaflet_length2
        count_leaflets -=2
    if count_leaflets == 1:
        leaflets.append(Translated((0,0,total_petiole_leaflet),leaflet))
    leafshape_fababean = Group(leaflets)
    return leafshape_fababean

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


# Create MTGs for rapeseed and fababean
def vegetative_rapeseed(
    DJ: int = 950,
    dict_params_rape = {},
    coord = (0,0,0)
    
    ):
    """ Build a field with nrows(coord) plants that have n_nodes internodes

    """
    growth_node = dict_params_rape['growth_node']
    phyllochrone = dict_params_rape['phylloc']
    n_nodes=int(round(DJ*phyllochrone))
    node_length = DJ * growth_node
    g = MTG()
    
    vid = g.add_component(g.root, label='Plant',edge_type='/',position=coord) #vid = vertex_id
    #vid = g.add_component(vid, label='Axis')

    #pid = g.add_component(vid, label='Phytomer') #pid= phytomer_id
    vid = g.add_child(vid, edge_type='<',label='Internode') 
    g.node(vid).NodeLength = node_length
    #g.node(vid).short = True
    leaf_id = g.add_child(vid, edge_type='+', label='Leaf')
    
    for i in range(n_nodes-1):
        vid = g.add_child(vid, edge_type='<', label='Internode') 
        g.node(vid).NodeLength = node_length
        #pid = g.add_child(pid, edge_type='<', label='Phytomer')
        #vid, pid = g.add_child_and_complex(vid, complex=pid, edge_type='<', label='Internode')
        #g.node(vid).NodeLength = node_length
        #g.node(vid).short = True

        leaf_id = g.add_child(vid, edge_type='+', label='Leaf')

    return g

def vegetative_rapeseed_plot(
    dict_params_rape,
    sowing_pattern,
    PlantAge_rape,
    vec_TLA_rape,
    iday):

    # initialize plot with 1st plant
    x0 = sowing_pattern['x'][0]*100
    y0 = sowing_pattern['y'][0]*100
    g0 = vegetative_rapeseed(DJ = PlantAge_rape,
                             dict_params_rape=dict_params_rape,
                             coord=[(x0,y0, 0)]).above 
    phenotype_rapeseed(g0,
        total_surface=vec_TLA_rape[iday],
        dict_params_rape=dict_params_rape)

    can = scene3d(g0,RapeseedVisitor)
    list_g = []
    mtgs = {}
    mtgs[0] = g0.properties()
    Temporary_res = g0.properties()
    list_g.append(g0)

    # iterate on other plants
    for i in range(1,len(sowing_pattern)):
        xi = sowing_pattern['x'][i]*100
        yi = sowing_pattern['y'][i]*100 
        gi = vegetative_rapeseed(DJ = PlantAge_rape,
                                 dict_params_rape=dict_params_rape,
                                 coord=[(xi,yi, 0)]).above 
        phenotype_rapeseed(gi,
            total_surface=vec_TLA_rape[iday],
            dict_params_rape=dict_params_rape)

        cani = scene3d(gi,RapeseedVisitor)
        list_g.append(gi)
        can = can + cani
        Temporary_res_i = gi.properties()
        Temporary_res = Temporary_res | Temporary_res_i
        mtgs[i] = gi.properties()
    return list_g, can, Temporary_res, mtgs


def total_height_fababean(DJ, dict_params_faba):
    L = dict_params_faba['L_height']
    k = dict_params_faba['k_height']
    x0 = dict_params_faba['x0_height']
    #L = 36
    #k = 0.1
    #x0 = 600
    total_height = L/(1+exp(-k*(DJ-x0)))
    return total_height

def vegetative_fababean(
    DJ: int = 950,
    #node_length: float= 0.02,
    dict_params_faba = {},
    coord = [(0,0,0)]
    
    ):
    """ Build a field with nrows(coord) plants that have n_nodes internodes

    """
    phyllochrone = dict_params_faba['phylloc']
    n_nodes=int(round(DJ*phyllochrone))
    total_height = total_height_fababean(DJ,dict_params_faba)
    node_length = total_height / n_nodes # equal height distribution among internodes

    g = MTG()
    vid = g.add_component(g.root,
                          label='Plant',
                          edge_type='/',
                          position=coord) #vid = vertex_id
    
    vid = g.add_child(vid, edge_type='<',label='Internode') 
    g.node(vid).NodeLength = node_length
    leaf_id = g.add_child(vid, edge_type='+', label='Leaf')
    
    for i in range(n_nodes-1):
        vid = g.add_child(vid, edge_type='<', label='Internode')
        g.node(vid).NodeLength = node_length
        leaf_id = g.add_child(vid, edge_type='+', label='Leaf')

    return g

def vegetative_fababean_plot(
    dict_params_faba,
    sowing_pattern,
    PlantAge_faba,
    vec_TLA_faba,
    iday):


    # initialize plot with 1st plant
    x0 = sowing_pattern['x'][0]*100
    y0 = sowing_pattern['y'][0]*100
    g0 = vegetative_fababean(DJ = PlantAge_faba,
                             dict_params_faba=dict_params_faba,
                             coord=[(x0,y0, 0)]).above 
    phenotype_fababean(g0,
        total_surface=vec_TLA_faba[iday],
        dict_params_faba=dict_params_faba) 
    
    can = scene3d(g0,FababeanVisitor)
    list_g = []
    mtgs = {}
    mtgs[0] = g0.properties()
    Temporary_res = g0.properties()
    list_g.append(g0)

    # iterate on other plants
    for i in range(1,len(sowing_pattern)):
        xi = sowing_pattern['x'][i]*100
        yi = sowing_pattern['y'][i]*100 
        gi = vegetative_fababean(DJ = PlantAge_faba,
                             dict_params_faba=dict_params_faba,
                             coord=[(xi,yi, 0)]).above 
        phenotype_fababean(gi,
            total_surface=vec_TLA_faba[iday],
            dict_params_faba=dict_params_faba)

        cani = scene3d(gi,FababeanVisitor)
        list_g.append(gi)
        can = can + cani
        Temporary_res_i = gi.properties()
        Temporary_res = Temporary_res | Temporary_res_i
        mtgs[i] = gi.properties()
    return list_g, can, Temporary_res, mtgs

def vegetative_mixture_plot(
    dict_params_rape,
    dict_params_faba,
    sowing_pattern,
    PlantAge_rape,
    PlantAge_faba,
    vec_TLA_rape,
    vec_TLA_faba,
    iday):

    list_g = []

    # initialize plot with 1st plant
    x0 = sowing_pattern['x'][0]*100
    y0 = sowing_pattern['y'][0]*100
    if sowing_pattern['species'][0] == "Fababean":
        g0 = vegetative_fababean(DJ = PlantAge_faba,
                                 dict_params_faba=dict_params_faba,
                                coord=[(x0,y0, 0)]).above 
        phenotype_fababean(g0,
            total_surface=vec_TLA_faba[iday],
            dict_params_faba=dict_params_faba) 

        can = scene3d(g0,RapeseedVisitor)
        list_g = []
        mtgs = {}
        mtgs[0] = g0.properties()
        Temporary_res = g0.properties()
        list_g.append(g0)
    else:
        g0 = vegetative_rapeseed(DJ = PlantAge_rape,
                                 dict_params_rape=dict_params_rape,
                             coord=[(x0,y0, 0)]).above 
        phenotype_rapeseed(g0,
            total_surface=vec_TLA_rape[iday],   
            dict_params_rape=dict_params_rape) 

        can = scene3d(g0,RapeseedVisitor)
        list_g = []
        mtgs = {}
        mtgs[0] = g0.properties()
        Temporary_res = g0.properties()
        list_g.append(g0)

    # iterate on other plants
    for i in range(1,len(sowing_pattern)):
        xi = sowing_pattern['x'][i]*100
        yi = sowing_pattern['y'][i]*100

        if sowing_pattern['species'][i] == "Fababean":
            gi = vegetative_fababean(DJ = PlantAge_faba,
                                     dict_params_faba=dict_params_faba,
                                coord=[(xi,yi, 0)]).above 
            phenotype_fababean(gi,
                total_surface=vec_TLA_faba[iday],
                dict_params_faba=dict_params_faba)

            cani = scene3d(gi,FababeanVisitor)
            can = can + cani
            list_g = []
            mtgs = {}
            mtgs[0] = g0.properties()
            Temporary_res = g0.properties()
            list_g.append(g0)

        else:
            gi = vegetative_rapeseed(DJ = PlantAge_rape,
                                     dict_params_rape=dict_params_rape,
                                 coord=[(xi,yi, 0)]).above 
            phenotype_rapeseed(gi,
                total_surface=vec_TLA_rape[iday],
                dict_params_rape=dict_params_rape)

            cani = scene3d(gi,RapeseedVisitor)
            can = can + cani
            list_g = []
            mtgs = {}
            mtgs[0] = g0.properties()
            Temporary_res = g0.properties()
            list_g.append(g0)
    return list_g, can, Temporary_res, mtgs


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


def phenotype_rapeseed(g,
                       total_surface = 200,
                       dict_params_rape = {}): 
    """
    applies phenotypical attributes to an MTG based on parameters. 
        leaf_max : [float between 0 and 1] Expectation of the bell curve => Position of the biggest leaf along the stem.
        phyllot: [float, degrees] phyllotaxy angle 
        ins_angle: [float, degrees] insertion angle of the petiole
        leaf_angle: [float, degrees] angle of the flat of the leaf
        total_surface: [int, cm2] surface to be shared following the bell proportion
        coeff_width: [float] Leaf Width / Leaf Length ratio (limb only)
        coeff_petiole: [float] Petiole Length / Leaf Length 
        stem_d: [float, cm] stem diameter
        coeff_petiole_d : [float] petiole diameter / stem diameter ration 
    """
    leaf_max = dict_params_rape['rmax'] # float=0.6587057,
    skew = dict_params_rape['k'] # float=5,  
    phyllot = dict_params_rape['phyllot'] # float = 137.5,
    ins_angle = dict_params_rape['ins_angle'] # float = 60,
    leaf_angle = 80.0 #à mesurer expérimentallement 
    coeff_width = dict_params_rape['coeff_width_leaf'] #float =0.831562, 
    coeff_petiole = dict_params_rape['coeff_petiole_leaf'] #float =0.51017, #limb length to petiole length , 0.31017 length/whole leag length
    stem_d = 0.1
    coeff_petiole_d = 0.5

    sortie=dict()
    plants=[k for k, v in g.properties()['label'].items()  if v=='Plant']
    leaves=[k for k, v in g.properties()['label'].items()  if v=='Leaf']
    internodes=[k for k, v in g.properties()['label'].items()  if v=='Internode']
    
    sortie['coeff_width'] = dict(zip(plants,[coeff_width]*len(plants)))
    sortie['coeff_petiole_d'] = dict(zip(plants,[coeff_petiole_d]*len(plants)))
    sortie['stem_d'] = dict(zip(plants,[stem_d]*len(plants)))
    surface = bell_shaped_dist(total_area=1, nb_phy=int(len(leaves)/len(plants)), rmax=leaf_max, skewness=skew)
    sortie['SurfaceRepartition']=dict(zip(leaves,surface*len(leaves)))
    sortie['LeafSurface']=dict(zip(leaves,[element * total_surface for element in surface]*len(leaves)))
    


    sortie['LeafLength']= dict(zip(leaves,
             [2*(element/(coeff_width*pi))**(0.5) for element in sortie['LeafSurface'].values()]*len(leaves)))

    sortie['LeafWidth']=dict(zip(leaves,
                     [element *coeff_width for element in sortie['LeafLength'].values()]*len(leaves)))
    sortie['SurfTheo']=dict(zip(leaves,[pi*(element/2)*(coeff_width*element/2) for element in sortie['LeafLength'].values()]*len(leaves)))
    sortie['PetioleLength']=dict(zip(leaves,[element * coeff_petiole for element in sortie['LeafLength'].values()]*len(leaves)))
    
    sortie['InsertionAngle']=dict(zip(leaves,[ins_angle]*len(leaves)))
    sortie['LeafAngle']=dict(zip(leaves,[leaf_angle]*len(leaves)))
    sortie['Phyllotaxy']=dict(zip(internodes,[phyllot]*len(internodes)))
    sortie['Phyllotaxy'].update(dict(zip(leaves,[phyllot]*len(leaves))))

    sortie['StemDiam']=dict(zip(internodes,[stem_d]*len(internodes)))
    sortie['PetioleDiam']=dict(zip(leaves,[stem_d*coeff_petiole_d]*len(leaves)))


    update_MTG(g,sortie)

def phenotype_fababean(g,
                       total_surface: float=300,
                       dict_params_faba={}):
    """
    applies phenotypical attributes to an MTG based on parameters. 
        leaf_max : [float between 0 and 1] Expectation of the bell curve => Position of the biggest leaf along the stem.
        phyllot: [float, degrees] phyllotaxy angle 
        ins_angle: [float, degrees] insertion angle of the petiole
        leaf_angle: [float, degrees] angle of the flat of the leaf
        total_surface: [int, cm2] surface to be shared following the bell proportion
        coeff_width: [float] Leaf Width / Leaf Length ratio (limb only)
        coeff_petiole: [float] Petiole Length / Leaf Length 
        stem_d: [float, cm] stem diameter
        coeff_petiole_d : [float] petiole diameter / stem diameter ration 
    """

    leaf_max = dict_params_faba['rmax'] #float=0.6587057
    skew = dict_params_faba['k'] # float=5
    phyllot = dict_params_faba['phyllot'] # float = 163.5
    ins_angle = dict_params_faba['ins_angle'] # float = 60
    leaf_angle : float = 110 #à mesurer expérimentallement
    coeff_width1 = dict_params_faba['coeff_width_leaflet1'] # float =0.831562
    coeff_width2 = dict_params_faba['coeff_width_leaflet2'] # float =0.831562
    coeff_petiole_leaflet1 = dict_params_faba['coeff_petiole_leaflet1'] # float =0.51017, #limb length to petiole length , 0.31017 length/whole leag length
    coeff_petiole_leaflet2 = dict_params_faba['coeff_petiole_leaflet2'] # float =0.51017, #limb length to petiole length , 0.31017 length/whole leag length
    stem_d = 0.1
    coeff_petiole_d = 0.8

    sortie=dict()
    plants=[k for k, v in g.properties()['label'].items()  if v=='Plant']
    leaves=[k for k, v in g.properties()['label'].items()  if v=='Leaf']
    internodes=[k for k, v in g.properties()['label'].items()  if v=='Internode']
    ranks = [i for i in range(1,len(leaves)+1)]
    nb_leaflets = [get_nb_leaflets(ri) for ri in ranks]
    
    sortie['Nb_leaflets']=dict(zip(leaves, nb_leaflets))
    vec_coeff_width = [coeff_width1]*2 + [coeff_width2]*(len(leaves)-2)
    sortie['coeff_width'] = dict(zip(leaves, vec_coeff_width))
    #sortie['coeff_width'] = dict(zip(plants,[coeff_width]*len(plants)))
    sortie['coeff_petiole_d'] = dict(zip(leaves,[coeff_petiole_d]*len(leaves)))
    sortie['stem_d'] = dict(zip(leaves,[stem_d]*len(leaves)))
    surface = bell_shaped_dist(total_area=1, nb_phy=int(len(leaves)/len(plants)), rmax=leaf_max, skewness=skew)
    sortie['SurfaceRepartition']=dict(zip(surface,leaves))
    sortie['LeafSurface']=dict(zip(leaves,[element * total_surface for element in surface]))
    vec_leaflet_surface = [surface[i] * total_surface/nb_leaflets[i] for i in range(0,len(surface))]
    sortie['LeafletSurface']=dict(zip(leaves, vec_leaflet_surface))
    #sortie['LeafLength']= dict(zip(leaves,vec_leaflet_length))
    vec_leaflet_length = [2*(vec_leaflet_surface[i]/(vec_coeff_width[i]*pi))**(0.5) for i in range(0,len(vec_leaflet_surface))]
    #leaflet_length = [2*(element/(coeff_width*pi))**(0.5) for element in sortie['LeafletSurface'].values()]
    sortie['LeafletLength']= dict(zip(leaves,vec_leaflet_length))

    #sortie['LeafWidth']=dict(zip(leaves,
    #                 [element *coeff_width for element in sortie['LeafLength'].values()]*len(leaves)))
    vec_leaflet_width = [vec_leaflet_length[i] *vec_coeff_width[i] for i in range(0,len(vec_leaflet_length))]
    sortie['LeafletWidth']=dict(zip(leaves,vec_leaflet_width))
    vec_surftheo = [pi*(vec_leaflet_length[i]/2)*(vec_coeff_width[i]*vec_leaflet_length[i]/2)*nb_leaflets[i] for i in range(0,len(vec_leaflet_length))]
    sortie['SurfTheo']=dict(zip(leaves,vec_surftheo))
    sortie['PetioleLength1']=dict(zip(leaves,[element * coeff_petiole_leaflet1 for element in sortie['LeafletLength'].values()]))
    sortie['PetioleLength2']=dict(zip(leaves,[element * coeff_petiole_leaflet2 for element in sortie['LeafletLength'].values()]))    
    sortie['InsertionAngle']=dict(zip(leaves,[ins_angle]*len(leaves)))
    sortie['LeafAngle']=dict(zip(leaves,[leaf_angle]*len(leaves)))
    sortie['Phyllotaxy']=dict(zip(internodes,[phyllot]*len(internodes)))
    sortie['Phyllotaxy'].update(dict(zip(leaves,[0]*len(leaves))))

    sortie['StemDiam']=dict(zip(internodes,[stem_d]*len(internodes)))
    sortie['PetioleDiam']=dict(zip(leaves,[stem_d*coeff_petiole_d]*len(leaves)))
    
    update_MTG(g,sortie)


# 3D scenes generation

def RapeseedVisitor(
    g, 
    v, 
    turtle,
    ):
    """
    Visitor that can handle an MTG file with multiple plants 
    This function is called by the scene3D() function when creating the 3D scene
    
    g is an MTG tree. In contains all the geometrical information needed by the visitor 
    v is the ID of the vertex being generated (int)
    turtle is the turtle used to create the 3D space
    """
    
   
    #retrieve the node and its label 
    nid = g.node(v)
    label = g.label(v)
    turtle.setId(v)

    #if nid.parent() is None:#this is a new plant base
    #    p = nid.complex_at_scale(scale=1)
        #print('plant no',p)
    #    if 'position' in p.properties():
            #print (p.label, 'moving to ', p.position)
    #        turtle.move(list(map(float,p.position)))
    #    else:
    #        print('standing still')
    #        turtle.move(0,0,0)

        #if 'azimuth' in p.properties():
            #turtle.rollR(p.azimuth)
    if label != 'Plant':
        turtle.rollL(nid.Phyllotaxy)
    #turtle.rollL(137.5)

    if g.edge_type(v) == '+':
        
        turtle.setWidth(nid.PetioleDiam)
        if label == 'Leaf':
            
            leafscale = Vector3(1, nid.LeafWidth, nid.LeafLength)


        
        turtle.down(nid.InsertionAngle)
        
        turtle.setColor(2)

        turtle.F(nid.PetioleLength)

        turtle.setColor(3)
        
        turtle.down(nid.LeafAngle-nid.InsertionAngle)

        my_leaf = Scaled(leafscale, make_leafshape_rapeseed())
        turtle.customGeometry(my_leaf)


    if label == 'Internode':
        turtle.setWidth(nid.StemDiam)
        turtle.setColor(1)
        turtle.F(nid.NodeLength)



def FababeanVisitor(
    g, 
    v, 
    turtle,
    ):
    """
    Visitor that can handle an MTG file with multiple plants 
    This function is called by the scene3D() function when creating the 3D scene
    
    g is an MTG tree. In contains all the geometrical information needed by the visitor 
    v is the ID of the vertex being generated (int)
    turtle is the turtle used to create the 3D space
    """
    
   
    #retrieve the node and its label 
    nid = g.node(v)
    label = g.label(v)
    turtle.setId(v)
    plant_id = g.complex_at_scale(v,scale=1)
    coeff_width=g.node(plant_id).coeff_width
    coeff_petiole_d=g.node(plant_id).coeff_petiole_d
    stem_d=g.node(plant_id).stem_d
    
    #turtle.rollL(nid.Phyllotaxy)
    turtle.rollL(163.5)

    if g.edge_type(v) == '+':
        
        turtle.setWidth(nid.PetioleDiam)
        if label == 'Leaf':
            nb_leaflets = nid.Nb_leaflets
            leafscale = multi_leaflets(nb_leaflets=int(nb_leaflets),
                                       leaf_surface=nid.LeafSurface,
                                       coeff_width=nid.coeff_width,
                                       petiole_leaflet_length1=nid.PetioleLength1,
                                       petiole_leaflet_length2=nid.PetioleLength2,
                                       coeff_petiole_d=coeff_petiole_d,
                                       stem_d=stem_d)
        
        turtle.down(nid.InsertionAngle)
        
        turtle.setColor(2)

        my_leaf = leafscale
        turtle.customGeometry(my_leaf)


    if label == 'Internode':
        turtle.setWidth(nid.StemDiam)
        turtle.setColor(1)
        turtle.F(nid.NodeLength)


#Scene creation

def scene3d(g,select_visitor=RapeseedVisitor):
    """
    calls a PlantGL turtle to generate a 3D scene
    g is an MTG file
    """
    t = pgl.PglTurtle()
    # set colors 
    colors = dict()
    colors['Internode'] = (100, 100, 80)
    colors['Petiole'] = (100, 100, 80)
    colors['Leaf'] = (9, 82, 40)
    color = Color3(*colors['Internode'])
    t.setColorAt(1, color)
    color = Color3(*colors['Petiole'])
    t.setColorAt(2, color)
    color = Color3(*colors['Leaf'])
    t.setColorAt(3, color)

    max_scale = g.max_scale()

    vid = next(g.component_roots_at_scale_iter(g.root, scale=max_scale))

    scene = turtle.TurtleFrame(
        g, 
        visitor=select_visitor, turtle=t, gc=False, all_roots=True)
    
    return scene


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