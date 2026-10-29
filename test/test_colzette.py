import numpy as np
import pandas as pd
import pytest

from openalea.colzette.colzette import (Plant, bell_shaped_dist, compute_thermal_time, get_nb_leaflets,
                                        get_params_intercrop, update_MTG)


def test_get_nb_leaflets():

    n = get_nb_leaflets(10)
    assert n == 5


@pytest.mark.parametrize("rank, expected", [(1, 2), (6, 2), (7, 3), (8, 4), (9, 4), (10, 5), (25, 5)])
def test_get_nb_leaflets_all_ranks(rank, expected):
    assert get_nb_leaflets(rank) == expected


def test_compute_thermal_time():
    temp = pd.Series([10., -2., 5., 8., 12.])
    tt = compute_thermal_time(temp, idx_begin=0, Tb=0)
    # negative temperatures do not count, then cumulated
    np.testing.assert_allclose(tt, [10, 10, 15, 23, 35])


def test_compute_thermal_time_base_and_start():
    temp = pd.Series([10., 10., 10., 10.])
    tt = compute_thermal_time(temp, idx_begin=2, Tb=4)
    # nothing before idx_begin, then temperature above the base temperature only
    np.testing.assert_allclose(tt, [0, 0, 6, 12])


def test_compute_thermal_time_does_not_modify_input():
    temp = pd.Series([10., -2., 5.])
    compute_thermal_time(temp, idx_begin=1, Tb=0)
    np.testing.assert_allclose(temp, [10, -2, 5])


@pytest.mark.parametrize("nb_phy", [1, 5, 15])
def test_bell_shaped_dist(nb_phy):
    areas = bell_shaped_dist(total_area=300, nb_phy=nb_phy, rmax=0.6, skewness=5)
    assert len(areas) == nb_phy
    assert sum(areas) == pytest.approx(300)
    assert all(a > 0 for a in areas)


def test_bell_shaped_dist_maximum_position():
    areas = bell_shaped_dist(total_area=1, nb_phy=20, rmax=0.6, skewness=5)
    # biggest leaf at the relative position rmax along the stem
    assert (np.argmax(areas) + 1) / 20 == pytest.approx(0.6, abs=0.1)


def test_get_params_intercrop_one_simulation(params_file):
    params = get_params_intercrop("Rapeseed", "Fababean", params_file("Rapeseed"), params_file("Fababean"),
                                  "One simulation")
    assert set(params) == {"Rapeseed", "Fababean"}
    for p in ["coeff_width_leaf", "coeff_petiole_leaf", "ins_angle", "rmax", "k", "growth_node", "phyllot",
              "phylloc"]:
        assert p in params["Rapeseed"]
    for p in ["coeff_width_leaflet1", "coeff_width_leaflet2", "coeff_petiole_leaflet1", "coeff_petiole_leaflet2",
              "ins_angle", "rmax", "k", "L_height", "x0_height", "k_height", "phyllot", "phylloc"]:
        assert p in params["Fababean"]


def test_get_params_intercrop_keeps_first_value():
    df = pd.DataFrame({"Species": ["Rapeseed"] * 3, "Parameter": ["a", "a", "b"], "Value": [1., 2., 3.]})
    params = get_params_intercrop("Rapeseed", None, df, pd.DataFrame(), "One simulation")
    assert params == {"Rapeseed": {"a": 1., "b": 3.}}


def test_get_params_intercrop_doe():
    df = pd.DataFrame({"a": [1., 2.], "b": [3., 4.]})
    params = get_params_intercrop("Rapeseed", "Fababean", df, df, "DOE")
    assert params["Rapeseed"][1] == {"a": 2., "b": 4.}
    assert set(params) == {"Rapeseed", "Fababean"}


def test_update_mtg():
    g = Plant().above
    leaf = [v for v, label in g.property("label").items() if label == "Leaf"][0]
    update_MTG(g, {"LeafSurface": {leaf: 12.}})
    assert g.property("LeafSurface") == {leaf: 12.}
    update_MTG(g, {"LeafSurface": {leaf: 15.}})
    assert g.property("LeafSurface")[leaf] == 15.


def test_plant():
    plant = Plant(name="p1")
    assert plant.name == "p1"
    assert set(plant.above.property("label").values()) == {"Plant", "Internode", "Leaf"}
    assert set(plant.below.property("label").values()) == {"RSA", "Root", "Segment"}
