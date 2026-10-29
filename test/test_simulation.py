import pytest

from openalea.colzette.geometry import phenotype_rapeseed
from openalea.colzette.light import light_interception
from openalea.colzette.population import generate_population
from openalea.colzette.scene import create_scene, get_domain, sowing_map_monocrop
from openalea.colzette.simulation import run_static_mixture_simulation, run_static_simulation

DENSITY = 33
LIGHT = 1000.


@pytest.fixture(scope="module")
def lit_scene(params_rapeseed):
    pattern = sowing_map_monocrop(1.0, 1.0, DENSITY, "Rapeseed")
    mtgs, positions = generate_population(pattern, params_rapeseed, 400., 800., phenotype_rapeseed)
    scene, shapes_indexer = create_scene(mtgs, positions, pattern)
    domain = get_domain(DENSITY, len(pattern))
    cs, vec_eabs, vec_area, raw, agg = light_interception(scene, shapes_indexer, mtgs, LIGHT, domain)
    return dict(pattern=pattern, mtgs=mtgs, shapes_indexer=shapes_indexer, domain=domain, cs=cs,
                vec_eabs=vec_eabs, vec_area=vec_area, raw=raw, agg=agg)


def leaf_shapes(lit_scene, plant_index):
    g = lit_scene["mtgs"][plant_index]
    leaves = {v for v, lab in g.property("label").items() if lab == "Leaf"}
    return [i for i, vid in lit_scene["shapes_indexer"][plant_index].items() if vid in leaves]


def test_light_interception_outputs(lit_scene):
    n = len(lit_scene["pattern"])
    assert len(lit_scene["vec_eabs"]) == len(lit_scene["vec_area"]) == n
    assert all(e > 0 for e in lit_scene["vec_eabs"])
    assert set(lit_scene["agg"]) >= {"Eabs", "Ei", "area"}


def test_light_interception_per_plant_sums(lit_scene):
    agg = lit_scene["agg"]
    for plant_index in (0, 10):
        shapes = leaf_shapes(lit_scene, plant_index)
        # per-plant energy is the energy of its leaves (surfacic Eabs x area)
        assert lit_scene["vec_eabs"][plant_index] == pytest.approx(sum(agg["Eabs"][i] * agg["area"][i] for i in shapes))
        assert lit_scene["vec_area"][plant_index] == pytest.approx(sum(agg["area"][i] for i in shapes))


def test_light_interception_leaf_area(lit_scene):
    # 400 cm2 of leaves per plant, area in m2
    assert lit_scene["vec_area"][0] == pytest.approx(400e-4, rel=0.05)


def test_light_interception_energy_balance(lit_scene):
    (x0, y0), (x1, y1) = lit_scene["domain"]
    ground = (x1 - x0) * (y1 - y0) / 1e4  # m2
    absorbed = sum(lit_scene["vec_eabs"])
    # the canopy cannot absorb more than the light received by its ground area
    assert 0 < absorbed < LIGHT * ground
    agg = lit_scene["agg"]
    for i in agg["Eabs"]:
        assert 0 <= agg["Eabs"][i] <= agg["Ei"][i] + 1e-9
        # an organ cannot receive more than an unshaded horizontal surface, the light being vertical
        assert agg["Ei"][i] <= LIGHT * (1 + 1e-6)


def test_light_interception_proportional_to_light(params_rapeseed):
    pattern = sowing_map_monocrop(1.0, 1.0, DENSITY, "Rapeseed").head(4)
    mtgs, positions = generate_population(pattern, params_rapeseed, 400., 800., phenotype_rapeseed)
    domain = get_domain(DENSITY, 36)
    out = []
    for light in (500., 1000.):
        scene, shapes_indexer = create_scene(mtgs, positions, pattern)
        out.append(light_interception(scene, shapes_indexer, mtgs, light, domain)[1])
    # CARIBU exchanges its data through text files with limited precision
    assert out[1] == pytest.approx([2 * e for e in out[0]], rel=1e-4)


@pytest.fixture(scope="module")
def params(params_rapeseed, params_fababean):
    return {"Rapeseed": params_rapeseed, "Fababean": params_fababean}


def test_run_static_simulation(params):
    scene, cs, sub_dat, raw, agg = run_static_simulation(
        das=10, PlantAge=800., RG_daily=LIGHT, TLA=400., option_plants="plot", density=DENSITY,
        dict_params=params, species="Rapeseed")
    assert list(sub_dat.columns) == ["DAS", "TT", "Plant", "Species", "leaf_area", "Eabs"]
    assert len(sub_dat) == 36
    assert (sub_dat["DAS"] == 10).all() and (sub_dat["Species"] == "Rapeseed").all()
    assert (sub_dat["Eabs"] > 0).all()
    assert len(scene) > 0 and set(agg["Eabs"]) == {shape.id for shape in scene}


def test_run_static_simulation_single_plant(params):
    _, _, sub_dat, _, _ = run_static_simulation(
        das=10, PlantAge=800., RG_daily=LIGHT, TLA=400., option_plants="single", density=DENSITY,
        dict_params=params, species="Rapeseed")
    assert len(sub_dat) == 1 and sub_dat["Eabs"][0] > 0


def test_run_static_simulation_no_leaf(params):
    scene, cs, sub_dat, raw, agg = run_static_simulation(
        das=0, PlantAge=10., RG_daily=LIGHT, TLA=0.0, option_plants="plot", density=DENSITY,
        dict_params=params, species="Rapeseed")
    assert scene is None and cs is None and raw is None and agg is None
    assert (sub_dat["Eabs"] == 0).all() and (sub_dat["leaf_area"] == 0).all()


def test_run_static_mixture_simulation(params):
    scene, cs, sub_dat, raw, agg = run_static_mixture_simulation(
        das=10, RG_daily=LIGHT, density=DENSITY, dict_params=params, TLA_brassica=400., TLA_legume=200.,
        PlantAge_brassica=800., PlantAge_legume=600.)
    assert list(sub_dat.columns) == ["DAS", "TT_brassica", "TT_legume", "Plant", "Species", "leaf_area", "Eabs"]
    assert sub_dat["Species"].value_counts().to_dict() == {"Rapeseed": 18, "Fababean": 18}
    assert (sub_dat["Eabs"] > 0).all()
    mean_area = sub_dat.groupby("Species")["leaf_area"].mean()
    assert mean_area["Rapeseed"] == pytest.approx(400e-4, rel=0.05)


def test_run_static_mixture_simulation_no_leaf(params):
    scene, _, sub_dat, _, agg = run_static_mixture_simulation(
        das=0, RG_daily=LIGHT, density=DENSITY, dict_params=params, TLA_brassica=0.0, TLA_legume=0.0,
        PlantAge_brassica=10., PlantAge_legume=0.)
    assert scene is None and agg is None
    assert (sub_dat["Eabs"] == 0).all()
