import pytest

import openalea.plantgl.all as pgl

from openalea.colzette.geometry import (make_leaflet_shape_fababean, make_leaflet_shape_lentil,
                                        make_leafshape_camelina, make_leafshape_rapeseed, phenotype_fababean,
                                        phenotype_rapeseed, total_height_sigmoid, vegetative)


def labels(g, label):
    return [v for v, lab in g.property("label").items() if lab == label]


@pytest.mark.parametrize("make_shape", [make_leafshape_rapeseed, make_leafshape_camelina,
                                        make_leaflet_shape_fababean, make_leaflet_shape_lentil])
def test_leaf_shapes(make_shape):
    shape = make_shape(u=5, v=2)
    assert isinstance(shape, pgl.BezierPatch)
    assert shape.ustride == 5 and shape.vstride == 2


def test_vegetative_rapeseed(params_rapeseed):
    dj = 800
    g = vegetative(DJ=dj, dict_params=params_rapeseed, coord=[(1, 2, 0)], species="Rapeseed")
    n_nodes = int(round(dj * params_rapeseed["phylloc"]))
    assert len(labels(g, "Plant")) == 1
    assert len(labels(g, "Internode")) == n_nodes
    assert len(labels(g, "Leaf")) == n_nodes
    for vid in labels(g, "Internode"):
        assert g.node(vid).NodeLength == pytest.approx(dj * params_rapeseed["growth_node"])


def test_vegetative_fababean_height(params_fababean):
    dj = 600
    g = vegetative(DJ=dj, dict_params=params_fababean, species="Fababean")
    internodes = labels(g, "Internode")
    # the sigmoid total height is shared equally between internodes
    total = sum(g.node(vid).NodeLength for vid in internodes)
    assert total == pytest.approx(total_height_sigmoid(dj, params_fababean))


def test_total_height_sigmoid(params_fababean):
    L, x0 = params_fababean["L_height"], params_fababean["x0_height"]
    assert total_height_sigmoid(x0, params_fababean) == pytest.approx(L / 2)
    assert 0 < total_height_sigmoid(x0 - 100, params_fababean) < total_height_sigmoid(x0 + 100, params_fababean) < L


def test_phenotype_rapeseed(params_rapeseed):
    g = vegetative(DJ=800, dict_params=params_rapeseed, species="Rapeseed")
    phenotype_rapeseed(g, total_surface=500, dict_params_rape=params_rapeseed)
    leaves = labels(g, "Leaf")
    # the total leaf area is shared between leaves
    assert sum(g.property("LeafSurface")[v] for v in leaves) == pytest.approx(500)
    for v in leaves:
        assert g.property("InsertionAngle")[v] == params_rapeseed["ins_angle"]
        assert g.property("LeafWidth")[v] == pytest.approx(g.property("LeafLength")[v] * params_rapeseed["coeff_width_leaf"])
        # an ellipse of the leaf length and width has the leaf area
        assert g.property("SurfTheo")[v] == pytest.approx(g.property("LeafSurface")[v])


def test_phenotype_fababean(params_fababean):
    g = vegetative(DJ=600, dict_params=params_fababean, species="Fababean")
    phenotype_fababean(g, total_surface=300, dict_params_faba=params_fababean)
    leaves = labels(g, "Leaf")
    assert sum(g.property("LeafSurface")[v] for v in leaves) == pytest.approx(300)
    for v in leaves:
        # a leaf is made of Nb_leaflets leaflets sharing its area
        assert (g.property("LeafletSurface")[v] * g.property("Nb_leaflets")[v]
                == pytest.approx(g.property("LeafSurface")[v]))
        assert g.property("SurfTheo")[v] == pytest.approx(g.property("LeafSurface")[v])
