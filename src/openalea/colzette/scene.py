
import numpy as np
import pandas as pd

from functools import partial

from openalea.mtg import turtle as turt
from openalea.mtg.plantframe.turtle import visitor
from openalea.plantgl import all as pgl

from openalea.colzette.geometry import RapeseedVisitor, FababeanVisitor

def create_scene_one_species(list_of_MTGs, list_of_positions, visitor = RapeseedVisitor):
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
                                    visitor=visitor,
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

def create_scene(list_of_MTGs, list_of_positions, sowing_pattern, ustride=9, vstride=2):
    list_rotation = []
    shapes_indexer = {}
    unique_shape_id = 1
    turtle = turt.PglTurtle()
    final_scene = pgl.Scene()

    for plant_index in range(0,len(list_of_positions)):
        # print(plant_index)
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
            visitor = partial(RapeseedVisitor, ustride=ustride, vstride=vstride)
            scene = turt.TurtleFrame(new_MTG,
                                        visitor=visitor,
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

def get_domain(density, nb_plantes):
    inter_row = np.sqrt(1 / density)
    inter_plant = 1. / inter_row / density
    if nb_plantes == 1:
        nrow = 1
    else:
        nrow = np.max([1, int(np.sqrt(nb_plantes))])
    dx = inter_plant * 100
    dy = inter_row * 100
    nx = int(nb_plantes / nrow)
    ny = nrow
    domain = ((0, 0), (nx * dx, ny * dy))
    return domain

def sowing_map(
        length,
        width,
        density,
        type="monocrop_aviso"):
    """
    length, width : plot dimensions (m)
    density : plants per m²
    species1, species2 : names of the two species
    """

    species1 = "Rapeseed"
    species2 = "Fababean"

    pas = np.sqrt(1 / density)

    xs = np.arange(pas / 2, length, pas)
    ys = np.arange(pas / 2, width, pas)

    data = []

    if type == "monocrop_aviso" or type == "monocrop_vigo":
        for i, y in enumerate(ys):
            for x in xs:
                data.append((x, y, 'Rapeseed'))

    elif type == "monocrop_faba":
        for i, y in enumerate(ys):
            for x in xs:
                data.append((x, y, 'Fababean'))

    elif type == "intercrop_aviso_RRF" or type == "intercrop_vigo" or type == "intercrop_aviso_RF":
        for i, y in enumerate(ys):
            species = species1 if i % 2 == 0 else species2
            for x in xs:
                data.append((x, y, species))

    data2 = pd.DataFrame(data, columns=["x", "y", "species"])
    return data2

 # backward compatibility
create_rapeseed_scene=create_scene_one_species
create_fababean_scene = partial(create_scene_one_species, visitor = FababeanVisitor)
create_mixture_scene = create_scene
