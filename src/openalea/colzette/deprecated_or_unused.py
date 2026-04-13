# 3/24/26: Not sure does these function are deprecated because unused and call

import openalea.plantgl.all as pgl

from openalea.mtg.plantframe import turtle

from openalea.colzette.geometry import (
    vegetative_fababean, phenotype_fababean,
    vegetative_rapeseed, phenotype_rapeseed,
    RapeseedVisitor, FababeanVisitor)

def vegetative_fababean_plot(
        dict_params_faba,
        sowing_pattern,
        PlantAge_faba,
        vec_TLA_faba,
        iday):
    # initialize plot with 1st plant
    x0 = sowing_pattern['x'][0] * 100
    y0 = sowing_pattern['y'][0] * 100
    g0 = vegetative_fababean(DJ=PlantAge_faba,
                             dict_params=dict_params_faba,
                             coord=[(x0, y0, 0)]).above
    phenotype_fababean(g0,
                       total_surface=vec_TLA_faba[iday],
                       dict_params_faba=dict_params_faba)

    can = scene3d(g0, FababeanVisitor)
    list_g = []
    mtgs = {}
    mtgs[0] = g0.properties()
    Temporary_res = g0.properties()
    list_g.append(g0)

    # iterate on other plants
    for i in range(1, len(sowing_pattern)):
        xi = sowing_pattern['x'][i] * 100
        yi = sowing_pattern['y'][i] * 100
        gi = vegetative_fababean(DJ=PlantAge_faba,
                                 dict_params=dict_params_faba,
                                 coord=[(xi, yi, 0)]).above
        phenotype_fababean(gi,
                           total_surface=vec_TLA_faba[iday],
                           dict_params_faba=dict_params_faba)

        cani = scene3d(gi, FababeanVisitor)
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
    x0 = sowing_pattern['x'][0] * 100
    y0 = sowing_pattern['y'][0] * 100
    if sowing_pattern['species'][0] == "Fababean":
        g0 = vegetative_fababean(DJ=PlantAge_faba,
                                 dict_params=dict_params_faba,
                                 coord=[(x0, y0, 0)]).above
        phenotype_fababean(g0,
                           total_surface=vec_TLA_faba[iday],
                           dict_params_faba=dict_params_faba)

        can = scene3d(g0, RapeseedVisitor)
        list_g = []
        mtgs = {}
        mtgs[0] = g0.properties()
        Temporary_res = g0.properties()
        list_g.append(g0)
    else:
        g0 = vegetative_rapeseed(DJ=PlantAge_rape,
                                 dict_params=dict_params_rape,
                                 coord=[(x0, y0, 0)]).above
        phenotype_rapeseed(g0,
                           total_surface=vec_TLA_rape[iday],
                           dict_params_rape=dict_params_rape)

        can = scene3d(g0, RapeseedVisitor)
        list_g = []
        mtgs = {}
        mtgs[0] = g0.properties()
        Temporary_res = g0.properties()
        list_g.append(g0)

    # iterate on other plants
    for i in range(1, len(sowing_pattern)):
        xi = sowing_pattern['x'][i] * 100
        yi = sowing_pattern['y'][i] * 100

        if sowing_pattern['species'][i] == "Fababean":
            gi = vegetative_fababean(DJ=PlantAge_faba,
                                     dict_params=dict_params_faba,
                                     coord=[(xi, yi, 0)]).above
            phenotype_fababean(gi,
                               total_surface=vec_TLA_faba[iday],
                               dict_params_faba=dict_params_faba)

            cani = scene3d(gi, FababeanVisitor)
            can = can + cani
            list_g = []
            mtgs = {}
            mtgs[0] = g0.properties()
            Temporary_res = g0.properties()
            list_g.append(g0)

        else:
            gi = vegetative_rapeseed(DJ=PlantAge_rape,
                                     dict_params=dict_params_rape,
                                     coord=[(xi, yi, 0)]).above
            phenotype_rapeseed(gi,
                               total_surface=vec_TLA_rape[iday],
                               dict_params_rape=dict_params_rape)

            cani = scene3d(gi, RapeseedVisitor)
            can = can + cani
            list_g = []
            mtgs = {}
            mtgs[0] = g0.properties()
            Temporary_res = g0.properties()
            list_g.append(g0)
    return list_g, can, Temporary_res, mtgs


def vegetative_rapeseed_plot(
        dict_params_rape,
        sowing_pattern,
        PlantAge_rape,
        vec_TLA_rape,
        iday):
    # initialize plot with 1st plant
    x0 = sowing_pattern['x'][0] * 100
    y0 = sowing_pattern['y'][0] * 100
    g0 = vegetative_rapeseed(DJ=PlantAge_rape,
                             dict_params=dict_params_rape,
                             coord=[(x0, y0, 0)]).above
    phenotype_rapeseed(g0,
                       total_surface=vec_TLA_rape[iday],
                       dict_params_rape=dict_params_rape)

    can = scene3d(g0, RapeseedVisitor)
    list_g = []
    mtgs = {}
    mtgs[0] = g0.properties()
    Temporary_res = g0.properties()
    list_g.append(g0)

    # iterate on other plants
    for i in range(1, len(sowing_pattern)):
        xi = sowing_pattern['x'][i] * 100
        yi = sowing_pattern['y'][i] * 100
        gi = vegetative_rapeseed(DJ=PlantAge_rape,
                                 dict_params=dict_params_rape,
                                 coord=[(xi, yi, 0)]).above
        phenotype_rapeseed(gi,
                           total_surface=vec_TLA_rape[iday],
                           dict_params_rape=dict_params_rape)

        cani = scene3d(gi, RapeseedVisitor)
        list_g.append(gi)
        can = can + cani
        Temporary_res_i = gi.properties()
        Temporary_res = Temporary_res | Temporary_res_i
        mtgs[i] = gi.properties()
    return list_g, can, Temporary_res, mtgs


def scene3d(g, select_visitor=RapeseedVisitor):
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
    color = pgl.Color3(*colors['Internode'])
    t.setColorAt(1, color)
    color = pgl.Color3(*colors['Petiole'])
    t.setColorAt(2, color)
    color = pgl.Color3(*colors['Leaf'])
    t.setColorAt(3, color)

    max_scale = g.max_scale()

    vid = next(g.component_roots_at_scale_iter(g.root, scale=max_scale))

    scene = turtle.TurtleFrame(
        g,
        visitor=select_visitor, turtle=t, gc=False, all_roots=True)

    return scene

