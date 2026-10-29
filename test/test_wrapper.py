import json

import numpy as np
import pandas as pd
import pytest

from openalea.colzette import Colzette, scenario_intercrop_brassica_faba, scenario_monocrop_brassica
from openalea.colzette.wrapper import SCENARIOS



# Initialisation and parameters

@pytest.mark.parametrize("name", list(SCENARIOS))
def test_scenarios_init(name):
    c = Colzette(**SCENARIOS[name])
    species = [s for s in (c.specie_brassica, c.specie_legume) if s is not None]
    assert set(c.dict_params) == set(species)
    assert c.simulation_length == len(c.climatic_inputs) > 0


def test_climatic_inputs():
    clim = Colzette().climatic_inputs
    for column in ("TT_brassica", "TT_legume", "PAR"):
        assert not clim[column].isna().any()
    # thermal times are cumulated from sowing, the legume being sown later
    assert (clim["TT_brassica"].diff().dropna() >= 0).all()
    assert (clim["TT_legume"] <= clim["TT_brassica"]).all()
    assert clim["TT_legume"].iloc[0] == 0


def test_daily_inputs_follow_day_index():
    c = Colzette(**scenario_intercrop_brassica_faba)
    c.day_index = 50
    assert c.PlantAge_brassica == c.climatic_inputs["TT_brassica"].iloc[50]
    assert c.PlantAge_legume == c.climatic_inputs["TT_legume"].iloc[50]
    assert c.TLA_brassica == c._TLA_brassica[50]
    assert c.TLA_legume == c._TLA_legume[50]
    assert c.RG_daily > 0


def test_monocrop_has_no_legume_inputs():
    c = Colzette(**scenario_monocrop_brassica)
    assert c.PlantAge_legume is None and c.TLA_legume is None


def test_parameters_table():
    table = Colzette.parameters()
    assert list(table.columns) == ["Nom", "Description", "Défaut", "Min", "Max"]
    assert len(table) == 20
    assert set(table["Nom"]) == {f.name for f in Colzette._parameter_fields()}
    for _, row in table.iterrows():
        assert row["Défaut"] == getattr(Colzette, row["Nom"])


def test_default_parameters_applied():
    c = Colzette(**scenario_intercrop_brassica_faba)
    assert c.dict_params["Rapeseed"]["ins_angle"] == Colzette.ins_angle_brassica
    assert c.dict_params["Fababean"]["L_height"] == Colzette.L_height_legume


def test_parameter_values_applied():
    # regression: the class default used to be applied instead of the instance value
    c = Colzette(**scenario_intercrop_brassica_faba, ins_angle_brassica=20., phyllot_legume=150.)
    assert c.dict_params["Rapeseed"]["ins_angle"] == 20.
    assert c.dict_params["Fababean"]["phyllot"] == 150.
    assert Colzette().dict_params["Rapeseed"]["ins_angle"] == Colzette.ins_angle_brassica


# Running

def test_run_selected_days(monocrop, leaf_days, no_leaf_day):
    assert monocrop.times == [no_leaf_day] + leaf_days
    n = len(monocrop.times)
    assert len(monocrop.dfs) == len(monocrop.list_scene) == len(monocrop.list_cs) == n
    assert len(monocrop.list_raw) == len(monocrop.list_agg) == n
    assert monocrop.day_index == leaf_days[-1] + 1


def test_run_no_leaf_day(monocrop):
    assert monocrop.list_scene[0] is None and monocrop.list_agg[0] is None
    assert (monocrop.dfs[0]["Eabs"] == 0).all()


def test_run_single_day_is_independent(monocrop, leaf_days):
    # each day only depends on its own inputs: simulating it alone gives the same result
    c = Colzette(**scenario_monocrop_brassica)
    c.run(leaf_days[-1])
    assert c.times == [leaf_days[-1]]
    pd.testing.assert_frame_equal(c.dfs[0], monocrop.dfs[-1])


def test_run_remaining_days():
    c = Colzette(**scenario_monocrop_brassica)
    c.day_index = c.simulation_length - 1
    c.run()
    assert c.times == [c.simulation_length - 1]
    c.run()  # nothing left to simulate
    assert len(c.times) == 1


@pytest.mark.parametrize("das", [-1, 10_000, [5, 10_000]])
def test_run_out_of_period(das):
    c = Colzette()
    with pytest.raises(ValueError):
        c.run(das)
    assert c.times == []


def test_run_legume_monocrop(leaf_days):
    c = Colzette(**SCENARIOS["mono_legume"])
    c.run(leaf_days[-1])
    assert set(c.plant_outputs["Species"]) == {"Fababean"}
    assert (c.plant_outputs["absolute_energy"] > 0).all()
    with pytest.raises(KeyError):
        c.rapeseed_outputs


# Outputs

def test_outputs_before_run():
    c = Colzette()
    assert c.plant_outputs.empty and c.species_outputs.empty


def test_plant_outputs(monocrop, leaf_days):
    df = monocrop.plant_outputs
    assert {"DAS", "TT", "Plant", "Species", "leaf_area", "absolute_energy", "absolute_energy_cum"} <= set(df.columns)
    assert len(df) == 36 * len(monocrop.times)
    assert set(df["DAS"]) == set(monocrop.times)
    last = df[df["DAS"] == leaf_days[-1]].set_index("Plant")
    # cumulated over the simulated days
    total = df.groupby("Plant")["absolute_energy"].sum()
    pd.testing.assert_series_equal(last["absolute_energy_cum"], total, check_names=False)
    # leaf area of a plant is the input total leaf area (cm2 -> m2)
    assert last["leaf_area"].mean() == pytest.approx(monocrop._TLA_brassica[leaf_days[-1]] * 1e-4, rel=0.05)


def test_plant_outputs_energy_matches_organs(monocrop):
    # plant energies sum to the energy of all leaves of the scene
    agg = monocrop.list_agg[-1]
    scene_total = sum(agg["Eabs"][i] * agg["area"][i] for i in agg["Eabs"])
    plants_total = monocrop.dfs[-1]["Eabs"].sum()
    assert 0 < plants_total <= scene_total * (1 + 1e-9)


def test_species_outputs(intercrop, leaf_days):
    sp = intercrop.species_outputs
    plants = intercrop.plant_outputs
    assert {"TT_brassica", "TT_legume"} <= set(sp.columns)
    assert len(sp) == 2 * len(leaf_days)
    assert (sp["n_plants"] == 18).all()
    for _, row in sp.iterrows():
        sub = plants[(plants["DAS"] == row["DAS"]) & (plants["Species"] == row["Species"])]
        assert row["absolute_energy"] == pytest.approx(sub["absolute_energy"].sum())
        assert row["absolute_energy_mean"] == pytest.approx(sub["absolute_energy"].mean())
        assert row["leaf_area"] == pytest.approx(sub["leaf_area"].sum())
        assert row["absolute_energy_cum_plant"] == pytest.approx(row["absolute_energy_cum"] / row["n_plants"])


def test_species_shares(intercrop, leaf_days):
    rapeseed, faba = intercrop.rapeseed_outputs, intercrop.faba_outputs
    assert set(rapeseed["Species"]) == {"Rapeseed"} and set(faba["Species"]) == {"Fababean"}
    assert len(rapeseed) == len(faba) == len(leaf_days)


def test_missing_species(monocrop):
    assert len(monocrop.rapeseed_outputs) == len(monocrop.times)
    with pytest.raises(KeyError):
        monocrop.faba_outputs
    with pytest.raises(KeyError):
        monocrop.last_day_faba()


def test_last_day(intercrop, leaf_days):
    table = intercrop.last_day_rapeseed()
    assert len(table) == 1 and table["DAS"][0] == leaf_days[-1]
    value = intercrop.last_day_rapeseed("absolute_energy_cum_plant")
    assert isinstance(value, float) and value == table["absolute_energy_cum_plant"][0]
    assert intercrop.last_day_faba("absolute_energy_cum_plant") == intercrop.faba_outputs[
        "absolute_energy_cum_plant"].iloc[-1]
    assert intercrop.last_day_faba()["Species"].tolist() == ["Fababean"]


# 3D views

@pytest.fixture(scope="module")
def k3d():
    return pytest.importorskip("k3d")


def test_organ_mesh(monocrop):
    vertices, indices, attribute = monocrop._organ_mesh(-1, "Eabs")
    assert vertices.shape[1] == 3 and indices.shape[1] == 3
    assert len(attribute) == len(vertices)
    assert indices.max() < len(vertices)
    agg = monocrop.list_agg[-1]["Eabs"]
    # one value per organ
    assert set(np.unique(attribute)) <= {np.float32(v) for v in agg.values()}


def test_plot_scene(monocrop, k3d, leaf_days):
    plot = monocrop.plot_scene()
    organs, label = plot.objects
    assert plot.colorbar_object_id == organs.id
    assert organs.color_range == [float(organs.attribute.min()), float(organs.attribute.max())]
    assert label.text == f"Eabs, DAS {leaf_days[-1]}"


def test_plot_scene_variable_and_day(monocrop, k3d, leaf_days):
    plot = monocrop.plot_scene(day=1, variable="area")
    assert plot.objects[1].text == f"area, DAS {leaf_days[0]}"
    assert plot.objects[0].attribute.max() < 0.1  # organ areas in m2


def test_plot_scene_no_leaf_day(monocrop, k3d):
    with pytest.raises(ValueError):
        monocrop.plot_scene(day=0)


def test_plot_scene_html(monocrop, k3d):
    pytest.importorskip("IPython")
    view = monocrop.plot_scene(as_html=True, height=300)
    assert view.data.startswith("<iframe srcdoc=") and "height: 300px" in view.data


def test_animate_scene(monocrop, k3d, leaf_days):
    plot = monocrop.animate_scene(fps=4)
    organs, labels = plot.objects
    # days without leaves are skipped, time is the DAS
    assert sorted(organs.vertices, key=float) == [str(d) for d in leaf_days]
    assert labels.text == {str(d): f"Eabs, DAS {d}" for d in leaf_days}
    # common color range over the days
    assert organs.color_range == [float(min(a.min() for a in organs.attribute.values())),
                                  float(max(a.max() for a in organs.attribute.values()))]
    assert plot.colorbar_object_id == organs.id
    assert plot.time_interpolation is False
    assert plot.time == leaf_days[0]
    # one simulated day per update
    assert plot.fps == 4 and plot.time_speed == 4 * (leaf_days[1] - leaf_days[0])


def test_animate_scene_selected_days(monocrop, k3d, leaf_days):
    plot = monocrop.animate_scene(days=[2])
    assert list(plot.objects[0].vertices) == [str(leaf_days[-1])]


def test_animate_scene_no_leaf_day(monocrop, k3d):
    with pytest.raises(ValueError):
        monocrop.animate_scene(days=[0])


@pytest.mark.parametrize("autoplay", [True, False])
def test_animate_scene_html(monocrop, k3d, autoplay, leaf_days):
    pytest.importorskip("IPython")
    import html
    page = html.unescape(monocrop.animate_scene(as_html=True, autoplay=autoplay).data)
    # play/pause bar driving the animated days
    assert "colzette-player" in page
    assert f"(K3DInstance, {json.dumps(leaf_days)})" in page
    assert ("K3DInstance.startAutoPlay();" in page) == autoplay
