import pytest

from openalea.colzette.geometry import phenotype_rapeseed
from openalea.colzette.population import generate_mixture_population, generate_population
from openalea.colzette.scene import create_scene, get_domain, sowing_map_intercrop, sowing_map_monocrop

DENSITY = 33


def test_sowing_map_monocrop():
    pattern = sowing_map_monocrop(1.0, 1.0, DENSITY, "Rapeseed")
    assert list(pattern.columns) == ["x", "y", "species"]
    assert len(pattern) == 36  # 6 x 6 plants spaced sqrt(1 / 33) m apart
    assert set(pattern["species"]) == {"Rapeseed"}
    assert pattern[["x", "y"]].min().min() > 0 and pattern[["x", "y"]].max().max() < 1


@pytest.mark.parametrize("sowing_option", ["rows", "mixed"])
def test_sowing_map_intercrop(sowing_option):
    pattern = sowing_map_intercrop(1.0, 1.0, DENSITY, "Rapeseed", "Fababean", sowing_option)
    assert len(pattern) == 36
    # half of each species
    assert pattern["species"].value_counts().to_dict() == {"Rapeseed": 18, "Fababean": 18}


def test_sowing_map_intercrop_rows():
    pattern = sowing_map_intercrop(1.0, 1.0, DENSITY, "Rapeseed", "Fababean", "rows")
    # one species per row
    assert (pattern.groupby("y")["species"].nunique() == 1).all()


@pytest.mark.parametrize("density", [20, 33, 50])
def test_get_domain(density):
    pattern = sowing_map_monocrop(1.0, 1.0, density, "Rapeseed")
    n = len(pattern)
    (x0, y0), (x1, y1) = get_domain(density, n)
    assert (x0, y0) == (0, 0)
    # the periodic pattern covers the ground area of its plants (cm2)
    assert (x1 - x0) * (y1 - y0) == pytest.approx(n / density * 1e4, rel=0.15)
    # and contains them
    assert pattern["x"].max() * 100 < x1 and pattern["y"].max() * 100 < y1


def test_get_domain_single_plant():
    (_, _), (x1, y1) = get_domain(DENSITY, 1)
    assert x1 * y1 == pytest.approx(1e4 / DENSITY)


def test_generate_population(params_rapeseed):
    pattern = sowing_map_monocrop(1.0, 1.0, DENSITY, "Rapeseed").head(4)
    mtgs, positions = generate_population(pattern, params_rapeseed, 400., 800., phenotype_rapeseed)
    assert len(mtgs) == len(positions) == 4
    assert positions[1] == (pattern["x"][1] * 100, pattern["y"][1] * 100, 0)
    leaves = [v for v, lab in mtgs[0].property("label").items() if lab == "Leaf"]
    assert sum(mtgs[0].property("LeafSurface")[v] for v in leaves) == pytest.approx(400.)


def test_generate_mixture_population(params_rapeseed, params_fababean):
    pattern = sowing_map_intercrop(1.0, 1.0, DENSITY, "Rapeseed", "Fababean", "rows")
    mtgs, positions = generate_mixture_population(pattern, params_rapeseed, params_fababean,
                                                  400., 200., 800., 600.)
    assert len(mtgs) == len(pattern)
    for g, specie in zip(mtgs, pattern["species"]):
        leaves = [v for v, lab in g.property("label").items() if lab == "Leaf"]
        total = sum(g.property("LeafSurface")[v] for v in leaves)
        assert total == pytest.approx(400. if specie == "Rapeseed" else 200.)
        # only fababean leaves are made of leaflets
        assert ("Nb_leaflets" in g.properties()) == (specie == "Fababean")


def test_create_scene(params_rapeseed, params_fababean):
    pattern = sowing_map_intercrop(1.0, 1.0, DENSITY, "Rapeseed", "Fababean", "rows").head(8)
    mtgs, positions = generate_mixture_population(pattern, params_rapeseed, params_fababean,
                                                  400., 200., 800., 600.)
    scene, shapes_indexer = create_scene(mtgs, positions, pattern, ustride=5, vstride=2)
    ids = [shape.id for shape in scene]
    assert len(ids) == len(set(ids)) > 0  # unique shape ids over the whole scene
    assert set(shapes_indexer) == set(range(len(pattern)))
    # every shape belongs to one plant, and points to a vertex of its MTG
    assert sorted(i for plant in shapes_indexer.values() for i in plant) == sorted(ids)
    for plant_index, plant_shapes in shapes_indexer.items():
        assert set(plant_shapes.values()) <= set(mtgs[plant_index].vertices())
