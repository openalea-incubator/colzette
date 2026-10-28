
from openalea.caribu.CaribuScene import CaribuScene

def light_interception(final_scene, shapes_indexer, list_of_MTGs, RG_daily, domain, light_direction = (0, 0, -1)):
    zenith = [(RG_daily, light_direction)]
    cs = CaribuScene(scene=final_scene, light=zenith, scene_unit='cm', pattern=domain)
    raw, agg = cs.run(infinite=True, simplify=True, direct=True)

    Eabs = agg["Eabs"]
    area = agg["area"]

    vec_Eabs = []
    vec_area = []
    for plant_index in range(0, len(list_of_MTGs)):
        g = list_of_MTGs[plant_index]
        shapes_plant = shapes_indexer[plant_index]
        g_indices = g.properties()['label']
        g_indices_leaf = [k for k, v in g_indices.items() if v == 'Leaf']
        new_indices_leaf = [k for k, v in shapes_plant.items() if v in g_indices_leaf]

        new_indices_plant = shapes_plant.keys()
        Eabs_plant = {k: v for k, v in Eabs.items() if k in new_indices_plant}
        Eabs_leaves = {k: v for k, v in Eabs_plant.items() if k in new_indices_leaf}
        area_plant = {k: v for k, v in area.items() if k in new_indices_plant}
        area_leaves = {k: v for k, v in area_plant.items() if k in new_indices_leaf}

        # Eabs is a surfacic density (light unit per m2) and area is in m2, so this is the energy absorbed by the plant leaves
        intercepted_light = sum([Eabs_leaves[k] * area_leaves[k] for k in Eabs_leaves])
        vec_Eabs.append(intercepted_light)
        vec_area.append(sum(area_leaves.values()))  # in m2
    return cs, vec_Eabs, vec_area, raw, agg
