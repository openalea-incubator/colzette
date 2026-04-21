"""
colzette module related turtle and visitor to build plant geometry
"""

import numpy as np

from math import pi, radians
from functools import partial

import openalea.plantgl.all as pgl
from openalea.mtg import MTG

from openalea.colzette.colzette import update_MTG, bell_shaped_dist, get_nb_leaflets

def RapeseedVisitor(
        g,
        v,
        turtle,
        ustride=9,
        vstride=2,
):
    '''
    Visitor that can handle an MTG file with multiple Rapeseed plants
    This function is called by the scene3D() function when creating the 3D scene

    :param g: (MTG) - In contains all the geometrical information needed by the visitor
    :param v: (int) - the ID of the vertex being generated
    :param turtle: turtle used to create the 3D space
    :param ustride: (int) - number of triangles in u direction
    :param vstride: (int) - number of triangles in v direction
    '''

    # retrieve the node and its label
    nid = g.node(v)
    label = g.label(v)
    turtle.setId(v)

    # if nid.parent() is None:#this is a new plant base
    #    p = nid.complex_at_scale(scale=1)
    # print('plant no',p)
    #    if 'position' in p.properties():
    # print (p.label, 'moving to ', p.position)
    #        turtle.move(list(map(float,p.position)))
    #    else:
    #        print('standing still')
    #        turtle.move(0,0,0)

    # if 'azimuth' in p.properties():
    # turtle.rollR(p.azimuth)
    if label != 'Plant':
        turtle.rollL(nid.Phyllotaxy)
    # turtle.rollL(137.5)

    if g.edge_type(v) == '+':

        turtle.setWidth(nid.PetioleDiam)
        if label == 'Leaf':
            leafscale = pgl.Vector3(1, nid.LeafWidth, nid.LeafLength)

        turtle.down(nid.InsertionAngle)

        turtle.setColor(2)

        turtle.F(nid.PetioleLength)

        turtle.setColor(3)

        turtle.down(nid.LeafAngle - nid.InsertionAngle)

        my_leaf = pgl.Scaled(leafscale, make_leafshape_rapeseed(u = ustride, v = vstride))
        turtle.customGeometry(my_leaf)

    if label == 'Internode':
        turtle.setWidth(nid.StemDiam)
        turtle.setColor(1)
        turtle.F(nid.NodeLength)


def FababeanVisitor(
        g,
        v,
        turtle,
        ustride=9,
        vstride=2,
):
    '''
    Visitor that can handle an MTG file with multiple Fababean plants
    This function is called by the scene3D() function when creating the 3D scene

    :param g: (MTG) - In contains all the geometrical information needed by the visitor
    :param v: (int) - the ID of the vertex being generated
    :param turtle: turtle used to create the 3D space
    :param ustride: (int) - number of triangles in u direction
    :param vstride: (int) - number of triangles in v direction
    '''

    # retrieve the node and its label
    nid = g.node(v)
    label = g.label(v)
    turtle.setId(v)
    plant_id = g.complex_at_scale(v, scale=1)
    coeff_width = g.node(plant_id).coeff_width
    coeff_petiole_d = g.node(plant_id).coeff_petiole_d
    stem_d = g.node(plant_id).stem_d

    # turtle.rollL(nid.Phyllotaxy)
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
                                       stem_d=stem_d,
                                       ustride=ustride,
                                       vstride=vstride)

        turtle.down(nid.InsertionAngle)

        turtle.setColor(2)

        my_leaf = leafscale
        turtle.customGeometry(my_leaf)

    if label == 'Internode':
        turtle.setWidth(nid.StemDiam)
        turtle.setColor(1)
        turtle.F(nid.NodeLength)


def multi_leaflets(nb_leaflets=5.0,
                   leaf_surface=1.0,
                   coeff_width=0.7,
                   petiole_leaflet_length1=2.0,
                   petiole_leaflet_length2=2.0,
                   coeff_petiole_d=0.5,
                   stem_d=0.035,
                   ustride=9,
                   vstride=2):
    surface_leaflet = leaf_surface/nb_leaflets # each leaflet has the same surface
    leaflet_length=2*(surface_leaflet/(coeff_width*pi))**(0.5)
    leaflet_width=leaflet_length*coeff_width
    leafscale = pgl.Vector3(1, leaflet_width, leaflet_length)
    leafletshape_fababean = make_leaflet_shape_fababean(u=ustride, v=vstride)
    leaflet = pgl.Scaled(leafscale,leafletshape_fababean)

    if nb_leaflets < 2:
        nb_petiole = 1
    else:
        nb_petiole = (nb_leaflets)//2
    total_petiole_leaflet = petiole_leaflet_length1 + petiole_leaflet_length2*(nb_petiole-1)
    petiole = pgl.Cylinder(radius=stem_d*coeff_petiole_d/2,height=total_petiole_leaflet)
    leaflet_left = pgl.AxisRotated(axis=(1,0,0),angle=-radians(60),geometry=leaflet)
    leaflet_right = pgl.AxisRotated(axis=(1,0,0),angle=radians(60),geometry=leaflet)
    leaflets = [petiole]
    translate = [0,0,petiole_leaflet_length1]
    count_leaflets = nb_leaflets
    leaflets.append(pgl.Translated(translate,leaflet_left))
    leaflets.append(pgl.Translated(translate,leaflet_right))
    for i in range(nb_petiole):
        leaflets.append(pgl.Translated(translate,leaflet_left))
        leaflets.append(pgl.Translated(translate,leaflet_right))
        translate[2] += petiole_leaflet_length2
        count_leaflets -=2
    if count_leaflets == 1:
        leaflets.append(pgl.Translated((0,0,total_petiole_leaflet),leaflet))
    leafshape_fababean = pgl.Group(leaflets)
    return leafshape_fababean

# Functions to generate leaf shapes (with leaflets for Fababean)
def make_leafshape_rapeseed(u=9, v=2):
    sc_factor = 3.572567770618656
    pts = lambda x,y,z : pgl.Vector4(x/sc_factor,y/sc_factor,z/sc_factor,1.0)
    r1=[pts(0,0,0), pts(7,-0.5,1), pts(3,-3,2), pts(1.5,-5,2.75), pts(-1,0,3)]
    r2=[pts(0,0,0), pts(7,0.5,1), pts(3,3,2), pts(1.5,5,2.75), pts(-1,0,3)]
    m=pgl.Point4Matrix([r1,r2])
    leafshape_rapeseed=pgl.BezierPatch(m, ustride=u, vstride=v)
    return(leafshape_rapeseed)

#original
def make_leafshape_rapeseed_original(u=9, v=2):
    sc_factor = 3.54673835885395
    pts = lambda x,y,z : pgl.Vector4(x/sc_factor,y/sc_factor,z/sc_factor,1.0)
    r1=[pts(0,0,0), pts(5,-0.5,1), pts(5,-3,2), pts(-1,-5,2.75), pts(-1,0,3)]
    r2=[pts(0,0,0), pts(5,0.5,1), pts(5,3,2), pts(-1,5,2.75), pts(-1,0,3)]
    m=pgl.Point4Matrix([r1,r2])
    leafshape_rapeseed=pgl.BezierPatch(m, ustride=u, vstride=v)
    return(leafshape_rapeseed)

def make_leaflet_shape_fababean(u=9, v=2):
    sc_factor = 3.173
    pts = lambda x,y,z : pgl.Vector4(x/sc_factor,y/sc_factor,z/sc_factor,1.0)
    r1=[pts(0,0,0), pts(0,-1,0.1), pts(0,-2,1), pts(0,-3,2), pts(0,-1,3), pts(0,-1,3.9), pts(0,0,4)]
    r2=[pts(0,0,0), pts(0,1,0.1),  pts(0,2,1),  pts(0,3,2),  pts(0,1,3),  pts(0,1,3.9),  pts(0,0,4)]
    m=pgl.Point4Matrix([r1,r2])
    leafletshape_fababean=pgl.BezierPatch(m, ustride=u, vstride=v)
    return(leafletshape_fababean)

# Create MTGs for rapeseed and Fababean
def vegetative(
        DJ: int = 950,
        dict_params={},
        coord=[(0, 0, 0)],
        species ='Fababean'
):
    """ Build a field with nrows(coord) plants that have n_nodes internodes

    """
    phyllochrone = dict_params['phylloc']
    n_nodes = int(round(DJ * phyllochrone))
    if species == 'Fababean':
        total_height = total_height_fababean(DJ, dict_params)
        if n_nodes > 0.0:
            node_length = total_height / n_nodes  # equal height distribution among internodes
        else:
            node_length = 0.0
    elif species == 'Rapeseed':
        growth_node = dict_params['growth_node']
        node_length = DJ * growth_node

    g = MTG()
    vid = g.add_component(g.root,
                          label='Plant',
                          edge_type='/',
                          position=coord)  # vid = vertex_id

    vid = g.add_child(vid, edge_type='<', label='Internode')
    g.node(vid).NodeLength = node_length
    leaf_id = g.add_child(vid, edge_type='+', label='Leaf')

    for i in range(n_nodes - 1):
        vid = g.add_child(vid, edge_type='<', label='Internode')
        g.node(vid).NodeLength = node_length
        leaf_id = g.add_child(vid, edge_type='+', label='Leaf')

    return g

def total_height_fababean(DJ, dict_params_faba):
    L = dict_params_faba['L_height']
    k = dict_params_faba['k_height']
    x0 = dict_params_faba['x0_height']
    # L = 36
    # k = 0.1
    # x0 = 600
    total_height = L / (1 + np.exp(-k * (DJ - x0)))
    return total_height

def phenotype_rapeseed(g,
                       total_surface=200,
                       dict_params_rape={}):
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
    leaf_max = dict_params_rape['rmax']  # float=0.6587057,
    skew = dict_params_rape['k']  # float=5,
    phyllot = dict_params_rape['phyllot']  # float = 137.5,
    ins_angle = dict_params_rape['ins_angle']  # float = 60,
    leaf_angle = 80.0  # à mesurer expérimentallement
    coeff_width = dict_params_rape['coeff_width_leaf']  # float =0.831562,
    coeff_petiole = dict_params_rape[
        'coeff_petiole_leaf']  # float =0.51017, #limb length to petiole length , 0.31017 length/whole leag length
    stem_d = 0.1
    coeff_petiole_d = 0.5

    output = dict()
    plants = [k for k, v in g.properties()['label'].items() if v == 'Plant']
    leaves = [k for k, v in g.properties()['label'].items() if v == 'Leaf']
    internodes = [k for k, v in g.properties()['label'].items() if v == 'Internode']

    output['coeff_width'] = dict(zip(plants, [coeff_width] * len(plants)))
    output['coeff_petiole_d'] = dict(zip(plants, [coeff_petiole_d] * len(plants)))
    output['stem_d'] = dict(zip(plants, [stem_d] * len(plants)))
    surface = bell_shaped_dist(total_area=1, nb_phy=int(len(leaves) / len(plants)), rmax=leaf_max, skewness=skew)
    output['SurfaceRepartition'] = dict(zip(leaves, surface * len(leaves)))
    output['LeafSurface'] = dict(zip(leaves, [element * total_surface for element in surface] * len(leaves)))

    output['LeafLength'] = dict(zip(leaves,
                                    [2 * (element / (coeff_width * pi)) ** (0.5) for element in
                                     output['LeafSurface'].values()] * len(leaves)))

    output['LeafWidth'] = dict(zip(leaves,
                                   [element * coeff_width for element in output['LeafLength'].values()] * len(leaves)))
    output['SurfTheo'] = dict(zip(leaves, [pi * (element / 2) * (coeff_width * element / 2) for element in
                                           output['LeafLength'].values()] * len(leaves)))
    output['PetioleLength'] = dict(
        zip(leaves, [element * coeff_petiole for element in output['LeafLength'].values()] * len(leaves)))

    output['InsertionAngle'] = dict(zip(leaves, [ins_angle] * len(leaves)))
    output['LeafAngle'] = dict(zip(leaves, [leaf_angle] * len(leaves)))
    output['Phyllotaxy'] = dict(zip(internodes, [phyllot] * len(internodes)))
    output['Phyllotaxy'].update(dict(zip(leaves, [phyllot] * len(leaves))))

    output['StemDiam'] = dict(zip(internodes, [stem_d] * len(internodes)))
    output['PetioleDiam'] = dict(zip(leaves, [stem_d * coeff_petiole_d] * len(leaves)))

    update_MTG(g, output)


def phenotype_fababean(g,
                       total_surface: float = 300,
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

    leaf_max = dict_params_faba['rmax']  # float=0.6587057
    skew = dict_params_faba['k']  # float=5
    phyllot = dict_params_faba['phyllot']  # float = 163.5
    ins_angle = dict_params_faba['ins_angle']  # float = 60
    leaf_angle: float = 110  # à mesurer expérimentallement
    coeff_width1 = dict_params_faba['coeff_width_leaflet1']  # float =0.831562
    coeff_width2 = dict_params_faba['coeff_width_leaflet2']  # float =0.831562
    coeff_petiole_leaflet1 = dict_params_faba[
        'coeff_petiole_leaflet1']  # float =0.51017, #limb length to petiole length , 0.31017 length/whole leag length
    coeff_petiole_leaflet2 = dict_params_faba[
        'coeff_petiole_leaflet2']  # float =0.51017, #limb length to petiole length , 0.31017 length/whole leag length
    stem_d = 0.1
    coeff_petiole_d = 0.8

    output = dict()
    plants = [k for k, v in g.properties()['label'].items() if v == 'Plant']
    leaves = [k for k, v in g.properties()['label'].items() if v == 'Leaf']
    internodes = [k for k, v in g.properties()['label'].items() if v == 'Internode']
    ranks = [i for i in range(1, len(leaves) + 1)]
    nb_leaflets = [get_nb_leaflets(ri) for ri in ranks]

    output['Nb_leaflets'] = dict(zip(leaves, nb_leaflets))
    vec_coeff_width = [coeff_width1] * 2 + [coeff_width2] * (len(leaves) - 2)
    output['coeff_width'] = dict(zip(leaves, vec_coeff_width))
    # output['coeff_width'] = dict(zip(plants,[coeff_width]*len(plants)))
    output['coeff_petiole_d'] = dict(zip(leaves, [coeff_petiole_d] * len(leaves)))
    output['stem_d'] = dict(zip(leaves, [stem_d] * len(leaves)))
    surface = bell_shaped_dist(total_area=1, nb_phy=int(len(leaves) / len(plants)), rmax=leaf_max, skewness=skew)
    output['SurfaceRepartition'] = dict(zip(surface, leaves))
    output['LeafSurface'] = dict(zip(leaves, [element * total_surface for element in surface]))
    vec_leaflet_surface = [surface[i] * total_surface / nb_leaflets[i] for i in range(0, len(surface))]
    output['LeafletSurface'] = dict(zip(leaves, vec_leaflet_surface))
    # output['LeafLength']= dict(zip(leaves,vec_leaflet_length))
    vec_leaflet_length = [2 * (vec_leaflet_surface[i] / (vec_coeff_width[i] * pi)) ** (0.5) for i in
                          range(0, len(vec_leaflet_surface))]
    # leaflet_length = [2*(element/(coeff_width*pi))**(0.5) for element in output['LeafletSurface'].values()]
    output['LeafletLength'] = dict(zip(leaves, vec_leaflet_length))

    # output['LeafWidth']=dict(zip(leaves,
    #                 [element *coeff_width for element in output['LeafLength'].values()]*len(leaves)))
    vec_leaflet_width = [vec_leaflet_length[i] * vec_coeff_width[i] for i in range(0, len(vec_leaflet_length))]
    output['LeafletWidth'] = dict(zip(leaves, vec_leaflet_width))
    vec_surftheo = [pi * (vec_leaflet_length[i] / 2) * (vec_coeff_width[i] * vec_leaflet_length[i] / 2) * nb_leaflets[i]
                    for i in range(0, len(vec_leaflet_length))]
    output['SurfTheo'] = dict(zip(leaves, vec_surftheo))
    output['PetioleLength1'] = dict(
        zip(leaves, [element * coeff_petiole_leaflet1 for element in output['LeafletLength'].values()]))
    output['PetioleLength2'] = dict(
        zip(leaves, [element * coeff_petiole_leaflet2 for element in output['LeafletLength'].values()]))
    output['InsertionAngle'] = dict(zip(leaves, [ins_angle] * len(leaves)))
    output['LeafAngle'] = dict(zip(leaves, [leaf_angle] * len(leaves)))
    output['Phyllotaxy'] = dict(zip(internodes, [phyllot] * len(internodes)))
    output['Phyllotaxy'].update(dict(zip(leaves, [0] * len(leaves))))

    output['StemDiam'] = dict(zip(internodes, [stem_d] * len(internodes)))
    output['PetioleDiam'] = dict(zip(leaves, [stem_d * coeff_petiole_d] * len(leaves)))

    update_MTG(g, output)

# backward compatibility
vegetative_fababean = vegetative
vegetative_rapeseed = partial(vegetative, species='Rapeseed')
