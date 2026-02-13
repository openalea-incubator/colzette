"""
SIMBAL shoot library
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
from itertools import cycle
from openalea.caribu.CaribuScene import CaribuScene

def illuminate(scene, light=None, pattern=None, scene_unit='cm', north=0):
    """Illuminate scene

    Args:
        scene: the scene (plantgl)
        light: lights. If None a vertical light is used
        pattern: the toric canopy pattern. If None, no pattern is used
        scene_unit: string indicating length unit in the scene (eg 'cm')
        north: the angle (deg, positive clockwise) from X+ to
         North (default: 0)

    Returns:

    """
    infinite = False
    if pattern is not None:
        infinite = True
    if light is not None:
        #light = light_sources(*light, orientation=north)
        light = [(light,(0,0,-1))] # zenith
    cs = CaribuScene(scene, light=light,scene_unit=scene_unit, pattern=pattern)
    raw, agg = cs.run(direct=True, simplify=True, infinite=infinite)
    return cs, raw['Ei'], pd.DataFrame(agg)

def build_scene(mtg, position=(0, 0, 0),
                     orientation=0,
                     leaf_material=None,
                     stem_material=None,
                     soil_material=None,
                     colors=None):
    """
    Returns a plantgl scene from an mtg.
    """
    if not isinstance(mtg, list):
        mtg = [mtg]
    if not isinstance(position, list):
        position=[position]
    if not isinstance(orientation, list):
        orientation=[orientation]
    if colors is None:
        if leaf_material is None:
            leaf_material = Material(Color3(0, 180, 0))
        if stem_material is None:
            stem_material = Material(Color3(0, 130, 0))
        if soil_material is None:
            soil_material = Material(Color3(170, 85, 0))
            # colors = g.property('color')


    scene = Scene()

    def geom2shape(vid, mesh, scene, colors, position, orientation, shape_id=None):
        shape = None
        if shape_id is None:
            shape_id = vid
        if isinstance(mesh, list):
            for m in mesh:
                geom2shape(vid, m, scene, colors, position, orientation)
            return
        if mesh is None:
            return
        if isinstance(mesh, Shape):
            shape = mesh
            mesh = mesh.geometry
        label = labels.get(vid)
        is_green = greeness.get(vid)
        mesh = Translated(position, AxisRotated((0,0,1),orientation, mesh))
        if colors:
            shape = Shape(mesh, Material(Color3(*colors.get(vid, [0, 0, 0]))))
        elif not greeness:
            if not shape:
                shape = Shape(mesh)
        elif label.startswith('Stem') and is_green:
            shape = Shape(mesh, stem_material)
        elif label.startswith('Leaf') and is_green:
            shape = Shape(mesh, leaf_material)
        elif not is_green:
            shape = Shape(mesh, soil_material)
        shape.id = shape_id

        scene.add(shape)

    nump = []
    count = 0
    for i, (g, p, o) in enumerate(zip(cycle(mtg), position, cycle(orientation))):
        geometries = g.property('geometry')
        greeness = g.property('is_green')
        labels = g.property('label')

        for vid, mesh in geometries.items():
            geom2shape(vid, mesh, scene, colors, p, o, vid+count)
            nump.append(i)
        count += len(g)

    return scene, nump


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

    if type == "monocrop_aviso" or type == "monocrop_aviso":
        for i, y in enumerate(ys):
            for x in xs:
                data.append((x, y, 'Rapeseed'))

    elif type == "monocrop_fababean":
        for i, y in enumerate(ys):
            for x in xs:
                data.append((x, y, 'Fababean'))

    elif type == "intercrop_aviso_RRF" or type == "intercrop_vigo_RRF" or type == "intercrop_aviso_RF" or type == "intercrop_vigo_RF" :
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


def multi_leaflets(nb_leaflets=5.0,leaf_surface=1.0, coeff_width=0.7, petiole_leaflet_length=2.0,coeff_petiole_d=0.5, stem_d=0.035):
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
    petiole = Cylinder(radius=stem_d*coeff_petiole_d/2,height=petiole_leaflet_length*nb_petiole)
    leaflet_left = AxisRotated(axis=(1,0,0),angle=-radians(60),geometry=leaflet)
    leaflet_right = AxisRotated(axis=(1,0,0),angle=radians(60),geometry=leaflet)
    leaflets = [petiole]
    translate = [0,0,petiole_leaflet_length]
    count_leaflets = nb_leaflets
    leaflets.append(Translated(translate,leaflet_left))
    leaflets.append(Translated(translate,leaflet_right))
    for i in range(nb_petiole):
        leaflets.append(Translated(translate,leaflet_left))
        leaflets.append(Translated(translate,leaflet_right))
        translate[2] += petiole_leaflet_length
        count_leaflets -=2
    if count_leaflets == 1:
        leaflets.append(Translated((0,0,petiole_leaflet_length*nb_petiole),leaflet))
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
        vid = g.add_component(vid, label='Axis')
        vid = g.add_component(vid, label='Phytomer')
        
        # Last scale
        vid = g.add_component(vid, label='Internode')
        leaf_id = g.add_child(vid, edge_type='+', label='Leaf')
        bud_id = g.add_component(vid, edge_type='<', label='Bud')

        fat_mtg(g)
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
    growth_node: float= 0.00034,
    phyllochrone = 0.015,
    coord = [(0,0,0)]
    
    ):
    """ Build a field with nrows(coord) plants that have n_nodes internodes

    """
    n_nodes=int(round(DJ*phyllochrone))
    node_length = DJ * growth_node
    above = g = MTG()


    for pl in coord:
       
        #print(pl)
        vid = g.add_component(g.root, label='Plant',edge_type='/',position=pl) #vid = vertex_id
        vid = g.add_component(vid, label='Axis')

        pid = g.add_component(vid, label='Phytomer') #pid= phytomer_id
        vid = g.add_component(pid, label='Internode') 
        g.node(vid).NodeLength = node_length
        #g.node(vid).short = True
        leaf_id = g.add_child(vid, edge_type='+', label='Leaf')
        
        for i in range(n_nodes-1):
            pid = g.add_child(pid, edge_type='<', label='Phytomer')
            vid, pid = g.add_child_and_complex(vid, complex=pid, edge_type='<', label='Internode')
            g.node(vid).NodeLength = node_length
            #g.node(vid).short = True

            leaf_id = g.add_child(vid, edge_type='+', label='Leaf')

    return Plant(name='rapeseed', above = above)

def vegetative_rapeseed_plot(
    growth_node_rape,
    phylloc_rape,
    sowing_pattern,
    PlantAge_rape,
    vec_TLA_rape,
    iday):

    # initialize plot with 1st plant
    x0 = sowing_pattern['x'][0]*100
    y0 = sowing_pattern['y'][0]*100
    g0 = vegetative_rapeseed(DJ = PlantAge_rape,
                             growth_node=growth_node_rape,
                             phyllochrone=phylloc_rape,
                             coord=[(x0,y0, 0)]).above 
    phenotype_rapeseed(g0,
        total_surface=vec_TLA_rape[iday],    
        leaf_max = 0.6,
        skew = 7,
        phyllot=137.5,
        ins_angle = 60,
        leaf_angle=60,
        coeff_width = 0.42,
        coeff_petiole = 0.41)

    can = scene3d(g0,RapeseedVisitor)

    mtgs = []
    mtgs.append(g0)

    positions = []
    positions.append((x0,y0,0))

    Temporary_res = g0.properties()

    # iterate on other plants
    for i in range(1,len(sowing_pattern)):
        xi = sowing_pattern['x'][i]*100
        yi = sowing_pattern['y'][i]*100 
        gi = vegetative_rapeseed(DJ = PlantAge_rape,
                                 growth_node=growth_node_rape,
                                 phyllochrone=0.016,
                                 coord=[(xi,yi, 0)]).above 
        positions.append((xi,yi,0))
        phenotype_rapeseed(gi,
            total_surface=vec_TLA_rape[iday],    
            leaf_max = 0.6,
            skew = 7,
            phyllot=137.5,
            ins_angle = 60,
            leaf_angle=60,
            coeff_width = 0.42,
            coeff_petiole = 0.41)

        cani = scene3d(gi,RapeseedVisitor)
        can = can + cani

        Temporary_res_i = gi.properties()
        Temporary_res = Temporary_res | Temporary_res_i

        mtgs.append(gi)
    return can, Temporary_res, mtgs, positions


def total_height_fababean(DJ):
    L = 36
    k = 0.1
    x0 = 600
    total_height = L/(1+exp(-k*(DJ-x0)))
    return total_height

def vegetative_fababean(
    DJ: int = 950,
    #node_length: float= 0.02,
    phyllochrone = 0.015,
    coord = [(0,0,0)]
    
    ):
    """ Build a field with nrows(coord) plants that have n_nodes internodes

    """
    n_nodes=int(round(DJ*phyllochrone))
    total_height = total_height_fababean(DJ)
    node_length = total_height / n_nodes # equal height distribution among internodes

    above = g = MTG()


    for pl in coord:
       
        #print(pl)
        vid = g.add_component(g.root, label='Plant',edge_type='/',position=pl) #vid = vertex_id
        vid = g.add_component(vid, label='Axis')

        pid = g.add_component(vid, label='Phytomer') #pid= phytomer_id
        vid = g.add_component(pid, label='Internode') 
        g.node(vid).NodeLength = node_length
        #g.node(vid).short = True
        leaf_id = g.add_child(vid, edge_type='+', label='Leaf')
        
        for i in range(n_nodes-1):
            pid = g.add_child(pid, edge_type='<', label='Phytomer')
            vid, pid = g.add_child_and_complex(vid, complex=pid, edge_type='<', label='Internode')
            g.node(vid).NodeLength = node_length
            #g.node(vid).short = True

            leaf_id = g.add_child(vid, edge_type='+', label='Leaf')

    return Plant(name='fababean', above = above)

def vegetative_fababean_plot(
    phylloc_faba,
    sowing_pattern,
    PlantAge_faba,
    vec_TLA_faba,
    iday):

    list_g = {}

    # initialize plot with 1st plant
    x0 = sowing_pattern['x'][0]*100
    y0 = sowing_pattern['y'][0]*100
    g0 = vegetative_fababean(DJ = PlantAge_faba,
                             phyllochrone=phylloc_faba,
                             coord=[(x0,y0, 0)]).above 
    phenotype_fababean(g0,
        total_surface=vec_TLA_faba[iday],    
        leaf_max = 0.61,
        skew = 1.48,
        phyllot=163.5,
        ins_angle = 40,
        leaf_angle=110,
        coeff_width = 0.7,
        coeff_petiole = 0.9,
        stem_d = 0.1,
        coeff_petiole_d = 0.8)
    list_g.append(g0)
    can = scene3d(g0,RapeseedVisitor)

    # iterate on other plants
    for i in range(1,len(sowing_pattern)):
        xi = sowing_pattern['x'][i]*100
        yi = sowing_pattern['y'][i]*100 
        gi = vegetative_fababean(DJ = PlantAge_faba,
                             phyllochrone=phylloc_faba,
                             coord=[(xi,yi, 0)]).above 
        phenotype_fababean(gi,
            total_surface=vec_TLA_faba[iday],    
            leaf_max = 0.61,
            skew = 1.48,
            phyllot=163.5,
            ins_angle = 40,
            leaf_angle=110,
            coeff_width = 0.7,
            coeff_petiole = 0.9,
            stem_d = 0.1,
            coeff_petiole_d = 0.8)

        cani = scene3d(gi,FababeanVisitor)
        list_g.append(gi)
        can = can + cani
    return list_g, can

def vegetative_mixture_plot(
    phylloc_rape,
    phylloc_faba,
    growth_node_rape,
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
                                phyllochrone=phylloc_faba,
                                coord=[(x0,y0, 0)]).above 
        phenotype_fababean(g0,
            total_surface=vec_TLA_faba[iday],    
            leaf_max = 0.61,
            skew = 1.48,
            phyllot=163.5,
            ins_angle = 40,
            leaf_angle=110,
            coeff_width = 0.7,
            coeff_petiole = 0.9,
            stem_d = 0.1,
            coeff_petiole_d = 0.8)
        list_g.append(g0)
        Temporary_res = g0.properties()
        can = scene3d(g0,RapeseedVisitor)
    else:
        g0 = vegetative_rapeseed(DJ = PlantAge_rape,
                             growth_node=growth_node_rape,
                             phyllochrone=phylloc_rape,
                             coord=[(x0,y0, 0)]).above 
        phenotype_rapeseed(g0,
            total_surface=vec_TLA_rape[iday],    
            leaf_max = 0.6,
            skew = 7,
            phyllot=137.5,
            ins_angle = 60,
            leaf_angle=60,
            coeff_width = 0.42,
            coeff_petiole = 0.41)

        list_g.append(g0)
        Temporary_res = g0.properties()
        can = scene3d(g0,RapeseedVisitor)

    # iterate on other plants
    for i in range(1,len(sowing_pattern)):
        xi = sowing_pattern['x'][i]*100
        yi = sowing_pattern['y'][i]*100

        if sowing_pattern['species'][i] == "Fababean":
            gi = vegetative_fababean(DJ = PlantAge_faba,
                                phyllochrone=phylloc_faba,
                                coord=[(xi,yi, 0)]).above 
            phenotype_fababean(gi,
                total_surface=vec_TLA_faba[iday],    
                leaf_max = 0.61,
                skew = 1.48,
                phyllot=163.5,
                ins_angle = 40,
                leaf_angle=110,
                coeff_width = 0.7,
                coeff_petiole = 0.9,
                stem_d = 0.1,
                coeff_petiole_d = 0.8)

            cani = scene3d(gi,FababeanVisitor)
            Temporary_res_i = gi.properties()
            Temporary_res = Temporary_res | Temporary_res_i
            list_g.append(gi)
            can = can + cani

        else:
            gi = vegetative_rapeseed(DJ = PlantAge_rape,
                                 growth_node=growth_node_rape,
                                 phyllochrone=phylloc_rape,
                                 coord=[(xi,yi, 0)]).above 
            phenotype_rapeseed(gi,
                total_surface=vec_TLA_rape[iday],    
                leaf_max = 0.6,
                skew = 7,
                phyllot=137.5,
                ins_angle = 60,
                leaf_angle=60,
                coeff_width = 0.42,
                coeff_petiole = 0.41)

            cani = scene3d(gi,RapeseedVisitor)
            Temporary_res_i = gi.properties()
            Temporary_res = Temporary_res | Temporary_res_i
            list_g.append(gi)
            can = can + cani
    return list_g, can, Temporary_res


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
    leaf_max: float=0.6587057,
    skew: float=5,  
    phyllot : float = 137.5,
    ins_angle : float = 60,
    leaf_angle : float = 80, #à mesurer expérimentallement 
    total_surface: float=300, 
    coeff_width: float =0.831562, 
    coeff_petiole: float =0.51017, #limb length to petiole length , 0.31017 length/whole leag length
    stem_d: float=0.1,
    coeff_petiole_d : float=0.5
    ): 
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
    sortie['Phyllotaxy'].update(dict(zip(leaves,[0]*len(leaves))))

    sortie['StemDiam']=dict(zip(internodes,[stem_d]*len(internodes)))
    sortie['PetioleDiam']=dict(zip(leaves,[stem_d*coeff_petiole_d]*len(leaves)))


    update_MTG(g,sortie)

def phenotype_fababean(g,
    leaf_max: float=0.6587057,
    skew: float=5,  
    phyllot : float = 137.5,
    ins_angle : float = 60,
    leaf_angle : float = 80, #à mesurer expérimentallement 
    total_surface: float=300, 
    coeff_width: float =0.831562, 
    coeff_petiole: float =0.51017, #limb length to petiole length , 0.31017 length/whole leag length
    stem_d: float=0.1,
    coeff_petiole_d : float=0.5
    ): 
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

    sortie=dict()
    plants=[k for k, v in g.properties()['label'].items()  if v=='Plant']
    leaves=[k for k, v in g.properties()['label'].items()  if v=='Leaf']
    internodes=[k for k, v in g.properties()['label'].items()  if v=='Internode']
    ranks = [i for i in range(1,len(leaves)+1)]
    nb_leaflets = [get_nb_leaflets(ri) for ri in ranks]
    
    sortie['Nb_leaflets']=dict(zip(leaves, nb_leaflets))
    sortie['coeff_width'] = dict(zip(plants,[coeff_width]*len(plants)))
    sortie['coeff_petiole_d'] = dict(zip(plants,[coeff_petiole_d]*len(plants)))
    sortie['stem_d'] = dict(zip(plants,[stem_d]*len(plants)))
    surface = bell_shaped_dist(total_area=1, nb_phy=int(len(leaves)/len(plants)), rmax=leaf_max, skewness=skew)
    sortie['SurfaceRepartition']=dict(zip(leaves,surface*len(leaves)))
    sortie['LeafSurface']=dict(zip(leaves,[element * total_surface for element in surface]*len(leaves)))
    sortie['LeafletSurface']=dict(zip(leaves,[surface[i] * total_surface/nb_leaflets[i] for i in range(0,len(surface))]*len(leaves)))
    sortie['LeafLength']= dict(zip(leaves,
             [2*(element/(coeff_width*pi))**(0.5) for element in sortie['LeafSurface'].values()]*len(leaves)))
    leaflet_length = [2*(element/(coeff_width*pi))**(0.5) for element in sortie['LeafletSurface'].values()]
    sortie['LeafletLength']= dict(zip(leaves,leaflet_length*len(leaves)))

    sortie['LeafWidth']=dict(zip(leaves,
                     [element *coeff_width for element in sortie['LeafLength'].values()]*len(leaves)))
    sortie['LeafletWidth']=dict(zip(leaves,
                    [element *coeff_width for element in sortie['LeafletLength'].values()]*len(leaves)))
    sortie['SurfTheo']=dict(zip(leaves,[pi*(leaflet_length[i]/2)*(coeff_width*leaflet_length[i]/2)*nb_leaflets[i] for i in range(0,len(leaflet_length))]*len(leaves)))
    sortie['PetioleLength']=dict(zip(leaves,[element * coeff_petiole for element in sortie['LeafletLength'].values()]*len(leaves)))
    
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

    if nid.parent() is None:#this is a new plant base
        p = nid.complex_at_scale(scale=1)
        #print('plant no',p)
        if 'position' in p.properties():
            #print (p.label, 'moving to ', p.position)
            turtle.move(list(map(float,p.position)))
        else:
            print('standing still')
            turtle.move(0,0,0)

        if 'azimuth' in p.properties():
            turtle.rollR(p.azimuth)
    
    turtle.rollL(nid.Phyllotaxy)
    #print(nid.Phyllotaxy)
    #turtle.rollL(137.5)

    if g.edge_type(v) == '+':
        
        turtle.setWidth(nid.PetioleDiam)
        if label == 'Leaf':
            
            leafscale = Vector3(1, nid.LeafWidth, nid.LeafLength)


        
        turtle.down(nid.InsertionAngle)
        
        turtle.setColor(2)

        #turtle.F(nid.PetioleLength)

        turtle.setColor(3)
        
        turtle.down(nid.LeafAngle-nid.InsertionAngle)

        my_leaf = Scaled(leafscale, make_leafshape_rapeseed())
        turtle.customGeometry(my_leaf)


    if label == 'Internode':
        turtle.setWidth(nid.StemDiam)
        turtle.setColor(1)
        turtle.F(nid.NodeLength)

    turtle.setId(v)


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
    plant_id = g.complex_at_scale(v,scale=1)
    coeff_width=g.node(plant_id).coeff_width
    coeff_petiole_d=g.node(plant_id).coeff_petiole_d
    stem_d=g.node(plant_id).stem_d

    if nid.parent() is None:#this is a new plant base
        p = nid.complex_at_scale(scale=1)
        if 'position' in p.properties():
            turtle.move(list(map(float,p.position)))
        else:
            print('standing still')
            turtle.move(0,0,0)

        if 'azimuth' in p.properties():
            turtle.rollR(p.azimuth)
    
    turtle.rollL(nid.Phyllotaxy)

    if g.edge_type(v) == '+':
        
        turtle.setWidth(nid.PetioleDiam)
        if label == 'Leaf':
            nb_leaflets = nid.Nb_leaflets
            leafscale = multi_leaflets(nb_leaflets=int(nb_leaflets), leaf_surface=nid.LeafSurface, coeff_width=coeff_width, petiole_leaflet_length=nid.PetioleLength,coeff_petiole_d=coeff_petiole_d, stem_d=stem_d)
        
        turtle.down(nid.InsertionAngle)
        
        turtle.setColor(2)

        my_leaf = leafscale
        turtle.customGeometry(my_leaf)


    if label == 'Internode':
        turtle.setWidth(nid.StemDiam)
        turtle.setColor(1)
        turtle.F(nid.NodeLength)

    turtle.setId(v)

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