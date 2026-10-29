import sys, os
import json
import pandas as pd
import numpy as np
from dataclasses import dataclass, field, fields

from pathlib import Path

from openalea.colzette.colzette import compute_thermal_time, get_params_intercrop
from openalea.colzette.simulation import run_static_simulation, run_static_mixture_simulation
from openalea.colzette.data import data_dir


# Play/pause button and day slider added to the standalone HTML view of Colzette.animate_scene,
# driving the k3d viewer (K3DInstance) through its public API; __TIMES__ is the list of animated DAS
_PLAYER_JS = """
(function (k3d, times) {
    var bar = document.createElement('div');
    bar.id = 'colzette-player';
    bar.style.cssText = 'position:absolute;left:8px;right:8px;bottom:8px;z-index:10;display:flex;'
        + 'align-items:center;gap:8px;padding:4px 8px;border-radius:4px;'
        + 'background:rgba(255,255,255,0.85);font:13px sans-serif;';
    var button = document.createElement('button');
    button.style.cssText = 'width:2.5em;cursor:pointer;';
    var slider = document.createElement('input');
    slider.type = 'range';
    slider.min = 0;
    slider.max = times.length - 1;
    slider.step = 1;
    slider.style.flex = '1';
    var label = document.createElement('span');
    bar.append(button, slider, label);
    document.body.appendChild(bar);
    // k3d colorbar is pinned at the bottom left (inline style): move it above the bar
    var style = document.createElement('style');
    style.textContent = '.colorMapLegend { bottom: 50px !important; }';
    document.head.appendChild(style);

    var playing = false;
    function showPlaying(state) {
        playing = state;
        button.textContent = state ? '\\u23F8' : '\\u25B6';
    }
    function showTime(t) {
        var i = 0;
        times.forEach(function (x, j) { if (Math.abs(x - t) < Math.abs(times[i] - t)) i = j; });
        slider.value = i;
        label.textContent = 'DAS ' + times[i];
    }
    button.onclick = function () { playing ? k3d.stopAutoPlay() : k3d.startAutoPlay(); };
    slider.oninput = function () { k3d.stopAutoPlay(); k3d.setTime(times[slider.value]); };
    k3d.on('autoPlayChange', showPlaying);
    k3d.on('timeChange', showTime);
    showPlaying(false);
    showTime(k3d.parameters.time);
})(K3DInstance, __TIMES__);
"""


def parameter(value, description: str, genre: str, min_value: float = None, max_value: float = None):
    return field(default=value, metadata=dict(
        description=description, genre=genre, min_value=min_value, max_value=max_value,
        variable_type="parameter"
    ))

SCENARIOS = {
    "mono_brassica": {
        "specie_brassica": "Rapeseed",
        "type_brassica": "intercrop_vigo",
        "specie_legume": None,
        "type_legume": None,
        "Type_simul": "monocrop_vigo",
        "sowing_option": "rows"
    },

    "mono_legume": {
        "specie_brassica": None,
        "type_brassica": None,
        "specie_legume": "Fababean",
        "type_legume": "intercrop_faba_vigo",
        "Type_simul": "monocrop_vigo",
        "sowing_option": "rows"
    },

    "intercrop": {
        "specie_brassica": "Rapeseed",
        "type_brassica": "intercrop_vigo",
        "specie_legume": "Fababean",
        "type_legume": "intercrop_faba_vigo",
        "Type_simul": "intercrop_vigo",
        "sowing_option": "rows"
    }
}

scenario_monocrop_brassica = SCENARIOS["mono_brassica"]
scenario_intercrop_brassica_faba = SCENARIOS["intercrop"]


@dataclass
class Colzette:
    # Hardcoded simulation hyperparameters which will not be played with during sensitivity analyses
    Type_simul: str = "monocrop_vigo"

    specie_brassica: str = "Rapeseed"

    type_brassica: str = "intercrop_aviso_RRF"

    specie_legume: str = None

    type_legume: str = None

    stand_option: str = 'plot'

    sowing_option: str = 'rows'

    density: int = 33

    # Parameters that can be varied

    # Brassica (Rapeseed)
    coeff_width_leaf_brassica: float = parameter(value=0.415592882407371,
                                        description="coefficient for leaf width",
                                        genre="brassica",
                                        min_value=0.37296365914787,
                                        max_value=0.464209515681673)
    coeff_petiole_leaf_brassica: float = parameter(value=0.351519470899816,
                                        description="coefficient for petiole to leaf ratio",
                                        genre="brassica",
                                        min_value=0.27816573556797,
                                        max_value=0.435530514559234)
    ins_angle_brassica: float = parameter(value=38.0823754789272,
                                        description="insertion angle (degrees)",
                                        genre="brassica",
                                        min_value=20.0,
                                        max_value=50.0)
    rmax_brassica: float = parameter(value=0.619420312123767,
                                        description="maximum relative growth rate",
                                        genre="brassica",
                                        min_value=0.559365582556123,
                                        max_value=0.661634100214167)
    k_brassica: float = parameter(value=7.42771083455965,
                                        description="curvature parameter",
                                        genre="brassica",
                                        min_value=3.27769994094298,
                                        max_value=10.3479955061558)
    growth_node_brassica: float = parameter(value=0.000342993585686865,
                                        description="internode growth coefficient",
                                        genre="brassica",
                                        min_value=0.000198487317705069,
                                        max_value=0.000443984789603443)
    phyllot_brassica: float = parameter(value=137.5,
                                        description="phyllotaxis angle (degrees)",
                                        genre="brassica",
                                        min_value=123.75,
                                        max_value=151.25)
    phylloc_brassica: float = parameter(value=0.0122709965423445,
                                        description="phyllochron",
                                        genre="brassica",
                                        min_value=0.0111022301134291,
                                        max_value=0.01344829163277)

    # Legume (Fababean)
    coeff_width_leaflet1_legume: float = parameter(value=0.690536840217465,
                                        description="coefficient for leaflet 1 width",
                                        genre="legume",
                                        min_value=0.642424242424242,
                                        max_value=0.744055944055944)
    coeff_width_leaflet2_legume: float = parameter(value=0.52576180667712,
                                        description="coefficient for leaflet 2 width",
                                        genre="legume",
                                        min_value=0.5,
                                        max_value=0.565217391304348)
    coeff_petiole_leaflet1_legume: float = parameter(value=0.233540714011381,
                                        description="coefficient for petiole to leaflet 1 ratio",
                                        genre="legume",
                                        min_value=0.181445603576751,
                                        max_value=0.324127264692886)
    coeff_petiole_leaflet2_legume: float = parameter(value=0.920480222899129,
                                        description="coefficient for petiole to leaflet 2 ratio",
                                        genre="legume",
                                        min_value=0.819672131147541,
                                        max_value=1.05660377358491)
    ins_angle_legume: float = parameter(value=37.7985074626866,
                                        description="insertion angle (degrees)",
                                        genre="legume",
                                        min_value=26.25,
                                        max_value=45.0)
    rmax_legume: float = parameter(value=0.65005192617206,
                                        description="maximum relative growth rate",
                                        genre="legume",
                                        min_value=0.583699525398067,
                                        max_value=0.746347200381635)
    k_legume: float = parameter(value=2.62971808931429,
                                        description="curvature parameter",
                                        genre="legume",
                                        min_value=1.16485781648376,
                                        max_value=2.49186625645388)
    L_height_legume: float = parameter(value=36.0056771131263,
                                        description="asymptotic plant height (cm)",
                                        genre="legume",
                                        min_value=23.1934536983573,
                                        max_value=48.8179005278954)
    x0_height_legume: float = parameter(value=548.304997985381,
                                        description="inflection point of height growth curve (degree-days)",
                                        genre="legume",
                                        min_value=208.89933885733,
                                        max_value=887.710657113431)
    k_height_legume: float = parameter(value=0.00950240141942771,
                                        description="steepness of height growth curve",
                                        genre="legume",
                                        min_value=-0.0164620794544861,
                                        max_value=0.0354668822933415)
    phyllot_legume: float = parameter(value=163.5,
                                        description="phyllotaxis angle (degrees)",
                                        genre="legume",
                                        min_value=147.15,
                                        max_value=179.85)
    phylloc_legume: float = parameter(value=0.0104583638185511,
                                        description="phyllochron",
                                        genre="legume",
                                        min_value=0.0100592630872002,
                                        max_value=0.0110270161896647)
    
    
    def __post_init__(self):
        # Import default parameter values
        if self.specie_brassica is not None:
            df_par_brassica = pd.read_csv(os.path.join(data_dir, "parameters", f"type_params_{self.specie_brassica.lower()}.csv"),sep='\t')
        else:
            df_par_brassica = pd.DataFrame()

        if self.specie_legume is not None:
            df_par_legume = pd.read_csv(os.path.join(data_dir, "parameters", f"type_params_{self.specie_legume.lower()}.csv"),sep='\t')
        else:
            df_par_legume = pd.DataFrame()

        self.dict_params = get_params_intercrop(self.specie_brassica, self.specie_legume, df_par_brassica, df_par_legume, "One simulation")
        
        # Superimpose parameter values from fields
        if self.specie_brassica is not None:
            brassica_parameters = [p for p in self._parameter_fields() if p.metadata["genre"] == "brassica"]
            for p in brassica_parameters:
                genre = p.metadata["genre"]
                p_name = p.name[:p.name.find(genre)-1]
                self.dict_params[self.specie_brassica][p_name] = getattr(self, p.name)
        
        if self.specie_legume is not None:
            legume_parameters = [p for p in self._parameter_fields() if p.metadata["genre"] == "legume"]
            for p in legume_parameters:
                genre = p.metadata["genre"]
                p_name = p.name[:p.name.find(genre)-1]
                self.dict_params[self.specie_legume][p_name] = getattr(self, p.name)

        # Importing climatic inputs from default path
        self.climatic_inputs = self.init_climatic_inputs()

        # Initialize time
        self.day_index = 0
        self.simulation_length = len(self.climatic_inputs)

        # Initialize output objects as attributes
        self.times = []
        self.dfs = []
        self.list_scene = []
        self.list_cs = []
        self.list_raw = []
        self.list_agg = []
        self.raw = None

        type(self).PlantAge_brassica = property(
            lambda self: self.climatic_inputs["TT_brassica"].iloc[self.day_index] if self.specie_brassica is not None else None
        )
        type(self).PlantAge_legume = property(
            lambda self: self.climatic_inputs["TT_legume"].iloc[self.day_index] if self.specie_legume is not None else None
        )
        type(self).RG_daily = property(
            lambda self: self.climatic_inputs["PAR"].iloc[self.day_index]
        )

        # Importing Total Leaf Area from default path
        TLA_fn = data_dir / 'input_leaf_surface' / 'set_TLA_IDEEV.csv'
        TLA_all = pd.read_csv(TLA_fn,sep="\t")
        if self.type_brassica is not None:
            TLA_indices_keep_brassica = TLA_all[TLA_all['Type']==self.type_brassica].index
            self._TLA_brassica = TLA_all['sim'].values[TLA_indices_keep_brassica]
        if self.type_legume is not None:
            TLA_indices_keep_legume = TLA_all[TLA_all['Type']==self.type_legume].index
            self._TLA_legume = TLA_all['sim'].values[TLA_indices_keep_legume]
        type(self).TLA_brassica = property(
            lambda self: self._TLA_brassica[self.day_index] if self.specie_brassica is not None else None
        )
        type(self).TLA_legume = property(
            lambda self: self._TLA_legume[self.day_index] if self.specie_legume is not None else None
        )

    

    def runner(self, das, RG_daily, density, dict_params,
               TLA_brassica=None, PlantAge_brassica=None,
               TLA_legume=None, PlantAge_legume=None,
               species_brassica='Rapeseed', species_legume=None,
               option_plants='plot', sowing_option='rows',
               Type_simul="intercrop_vigo", ustride=9, vstride=2,
               light_direction=(0, 0, -1)):
        if species_brassica is not None and species_legume is not None:
            scene, caribu_scene, sub_dat, raw, agg = run_static_mixture_simulation(
                das=das, RG_daily=RG_daily, density=density, dict_params=dict_params,
                TLA_brassica=TLA_brassica, TLA_legume=TLA_legume,
                PlantAge_brassica=PlantAge_brassica, PlantAge_legume=PlantAge_legume,
                species_brassica=species_brassica, species_legume=species_legume,
                sowing_option=sowing_option,
                Type_simul=Type_simul, ustride=ustride, vstride=vstride,
                light_direction=light_direction)
        elif species_brassica is not None:
            scene, caribu_scene, sub_dat, raw, agg = run_static_simulation(
                das=das, PlantAge=PlantAge_brassica, RG_daily=RG_daily, TLA=TLA_brassica,
                option_plants=option_plants, density=density, dict_params=dict_params,
                type_simul=Type_simul, species=species_brassica,
                ustride=ustride, vstride=vstride, light_direction=light_direction)
        else:
            scene, caribu_scene, sub_dat, raw, agg = run_static_simulation(
                das=das, PlantAge=PlantAge_legume, RG_daily=RG_daily, TLA=TLA_legume,
                option_plants=option_plants, density=density, dict_params=dict_params,
                type_simul=Type_simul, species=species_legume,
                ustride=ustride, vstride=vstride, light_direction=light_direction)
        return scene, caribu_scene, sub_dat, raw, agg

    def run(self, day=None):
        """Run the simulation.

        Without argument, simulates every remaining day. Each day only depends on its own inputs (thermal time,
        TLA, PAR), so das can be a single DAS or a list of DAS to simulate only those days: outputs keep the
        same structure, with one entry per simulated day (cumulated outputs then only sum the simulated days).
        """
        if day is None:
            days = list(range(self.day_index, self.simulation_length))
        else:
            days = [day] if np.isscalar(day) else list(day)
            for d in days:
                if not 0 <= d < self.simulation_length:
                    raise ValueError(f"DAS {d} out of the simulated period [0, {self.simulation_length - 1}]")
        for d in days:
            self.day_index = d
            self.__call__()
            self.log()
        if days:
            self.day_index = days[-1] + 1


    def __call__(self):
        self.scene, self.caribu_scene, self.sub_dat, self.raw, self.agg = self.runner(
            das=self.day_index,
            RG_daily=self.RG_daily,
            density=self.density,
            dict_params=self.dict_params,
            TLA_brassica=self.TLA_brassica,
            PlantAge_brassica=self.PlantAge_brassica,
            TLA_legume=self.TLA_legume,
            PlantAge_legume=self.PlantAge_legume,
            species_brassica=self.specie_brassica,
            species_legume=self.specie_legume,
            sowing_option=self.sowing_option,
            option_plants=self.stand_option,
            Type_simul=self.Type_simul, ustride=9, vstride=2, light_direction=(0, 0, -1))


    def log(self):
        # just to display running activity
        sys.stdout.write('\r')
        sys.stdout.write(f'Running {self.day_index/self.simulation_length*100:.0f}' + '%')  # pad to overwrite leftovers
        sys.stdout.flush()

        self.times.append(self.day_index)
        self.dfs.append(self.sub_dat)
        self.list_scene.append(self.scene)
        self.list_cs.append(self.caribu_scene)
        self.list_raw.append(self.raw)
        self.list_agg.append(self.agg)
    
    @classmethod
    def _parameter_fields(cls):
        fds = [f for f in fields(cls) if len(f.metadata) > 0]
        return [f for f in fds if f.metadata["variable_type"] == "parameter"]

    @classmethod
    def parameters(cls):
        rows = []
        for p in cls._parameter_fields():
            rows.append({
                "Nom": p.name,
                "Description": p.metadata["description"],
                "Défaut": p.default,
                "Min": p.metadata["min_value"],
                "Max": p.metadata["max_value"],
            })

        df = pd.DataFrame(rows)
        return df
    
    def init_climatic_inputs(self):
        """
        WARNING: hardcoded
        """
        meteo_fn = data_dir / 'climate' / 'IDEEV_2023_INRAE_STATION_91272001.csv'
        clim= pd.read_csv(meteo_fn,sep=";",skiprows=11)
        clim['TM'] = (clim['TN'] + clim['TX'])/2

        brassica = 0
        Tb_legume = 0
        idx_brassica = clim.index[
            (clim["AN"] == 2023) &
            (clim["MOIS"] == 9) &
            (clim["JOUR"] == 14)][0] # brassica sowing date 14/09/2023
        idx_legume = clim.index[
            (clim["AN"] == 2023) &
            (clim["MOIS"] == 9) &
            (clim["JOUR"] == 20)][0] # legume sowing date 14/09/2023
        clim2 = clim.iloc[idx_brassica:]
        clim2['TT_brassica'] = compute_thermal_time(vec_temp=clim2['TM'], idx_begin=0, Tb=brassica)
        clim2['TT_legume'] = compute_thermal_time(vec_temp=clim2['TM'], idx_begin=idx_legume-1, Tb=Tb_legume)
        return clim2

    @property
    def plant_outputs(self):
        """Per-plant time series: one row per plant and per simulated day.

        leaf_area is the plant leaf area (m2), absolute_energy the PAR absorbed by its leaves that day (J)
        and absolute_energy_cum its cumulated value since sowing.
        """
        if not self.dfs:
            return pd.DataFrame()
        df = pd.concat(self.dfs, ignore_index=True).rename(columns={"Eabs": "absolute_energy"})
        df["absolute_energy_cum"] = df.groupby("Plant")["absolute_energy"].cumsum()
        return df

    @property
    def species_outputs(self):
        """Per-species time series: one row per species and per simulated day.

        leaf_area and absolute_energy are summed over the plants of the species,
        absolute_energy_mean is the average per plant, absolute_energy_cum_plant its cumulated value since sowing.
        """
        df = self.plant_outputs
        if df.empty:
            return df
        keys = ["DAS"] + [c for c in df.columns if c.startswith("TT")] + ["Species"]
        sp = df.groupby(keys, as_index=False, dropna=False, sort=False).agg(
            n_plants=("Plant", "count"),
            leaf_area=("leaf_area", "sum"),
            leaf_area_mean=("leaf_area", "mean"),
            absolute_energy=("absolute_energy", "sum"),
            absolute_energy_mean=("absolute_energy", "mean"))
        sp["absolute_energy_cum"] = sp.groupby("Species")["absolute_energy"].cumsum()
        sp["absolute_energy_cum_plant"] = sp.groupby("Species")["absolute_energy_mean"].cumsum()
        return sp

    @property
    def rapeseed_outputs(self):
        specie = "Rapeseed"
        df = self.species_outputs
        if specie in df["Species"].values:
            return df[df["Species"] == specie]
        else:
            raise KeyError(f"No {specie} in the simulation")

    @property
    def faba_outputs(self):
        specie = "Fababean"
        df = self.species_outputs
        if specie in df["Species"].values:
            return df[df["Species"] == specie]
        else:
            raise KeyError(f"No {specie} in the simulation")

    def last_day_rapeseed(self, prop: str = None):
        df = self.rapeseed_outputs
        filtered = df[df["DAS"] == df["DAS"].max()].reset_index(drop=True)
        if prop is None:
            return filtered
        else:
            return float(filtered[prop].item())

    def last_day_faba(self, prop: str = None):
        df = self.faba_outputs
        filtered = df[df["DAS"] == df["DAS"].max()].reset_index(drop=True)
        if prop is None:
            return filtered
        else:
            return float(filtered[prop].item())

    def plot_scene(self, day=-1, variable="Eabs", color_map=None, plot=None, as_html=False, height=500):
        """3D view of the scene of a simulated day, each organ colored by its CARIBU output, with a colorbar.

        day is a position in the simulated days (as in self.times), -1 for the last one.
        variable is a key of the CARIBU aggregated outputs: "Eabs" (J/m2 of organ), "Ei", "area" (m2)...
        Returns a k3d plot, displayed when it is the last expression of a notebook cell.
        With as_html=True, returns instead a standalone HTML view, for notebook front-ends that do not render
        the k3d widget (e.g. VS Code).
        """
        import k3d

        if self.list_scene[day] is None:
            raise ValueError(f"Nothing to plot at DAS {self.times[day]}: no leaf area yet")
        vertices, indices, attribute = self._organ_mesh(day, variable)

        if plot is None:
            plot = k3d.plot()
        organs = k3d.mesh(vertices, indices, attribute=attribute,
                          color_map=color_map if color_map is not None else k3d.basic_color_maps.Jet,
                          color_range=[float(attribute.min()), float(attribute.max())],
                          side="double")
        plot += organs
        plot.colorbar_object_id = organs.id
        plot += k3d.text2d(f"{variable}, DAS {self.times[day]}", position=(0.01, 0.01), is_html=False)
        return self._k3d_output(plot, as_html, height)

    def animate_scene(self, variable="Eabs", days=None, color_map=None, plot=None, as_html=False, height=500,
                      fps=4, autoplay=True):
        """Same view as plot_scene, with a time slider over the simulated days.

        With as_html=True, a play/pause button and a slider over the simulated days are added at the bottom of
        the view, and with autoplay=True the animation loops as soon as it is displayed.
        The k3d widget only has its own controls, in its menu (top right: Controls > Animation, folder closed by
        default), and cannot start by itself: call .start_auto_play() on the returned plot once it is displayed.

        Time is the DAS; fps is the number of simulated days shown per second.
        days is a list of positions in the simulated days (as in self.times), default all days with leaves.
        The colorbar range is common to all days so that colors can be compared over time.
        Each day adds its whole geometry to the plot: subsample days (e.g. days=range(0, len(c.times), 7))
        to keep it light, especially with as_html=True.
        """
        import k3d

        if days is None:
            days = range(len(self.times))
        days = [d for d in days if self.list_scene[d] is not None]
        if not days:
            raise ValueError("Nothing to plot: no simulated day with leaf area")

        vertices, indices, attribute, labels = {}, {}, {}, {}
        for d in days:
            t = str(self.times[d])  # k3d time key, here the DAS
            vertices[t], indices[t], attribute[t] = self._organ_mesh(d, variable)
            labels[t] = f"{variable}, DAS {self.times[d]}"

        if plot is None:
            plot = k3d.plot()
        organs = k3d.mesh(vertices, indices, attribute=attribute,
                          color_map=color_map if color_map is not None else k3d.basic_color_maps.Jet,
                          color_range=[float(min(a.min() for a in attribute.values())),
                                       float(max(a.max() for a in attribute.values()))],
                          side="double")
        plot += organs
        plot.colorbar_object_id = organs.id
        plot += k3d.text2d(labels, position=(0.01, 0.01), is_html=False)
        # organs change from one day to the next: show the nearest simulated day instead of interpolating
        plot.time_interpolation = False
        plot.time = float(self.times[days[0]])
        # k3d updates the view fps times per second and advances time_speed DAS per second:
        # move by one simulated day at each update
        step = float(np.median(np.diff([self.times[d] for d in days]))) if len(days) > 1 else 1.0
        plot.fps = fps
        plot.time_speed = fps * step
        # run by the standalone HTML view once loaded, ignored by the k3d widget
        js = _PLAYER_JS.replace("__TIMES__", json.dumps([self.times[d] for d in days]))
        if autoplay:
            js += "K3DInstance.startAutoPlay();"
        return self._k3d_output(plot, as_html, height, js)

    def _organ_mesh(self, day, variable):
        """Vertices, triangles and per-vertex values of the organs of a simulated day, one value per organ."""
        from openalea.plantgl.all import Tesselator

        values = self.list_agg[day][variable]
        tesselator = Tesselator()
        vertices, indices, attribute = [], [], []
        for shape in self.list_scene[day]:
            if shape.id not in values:
                continue
            shape.geometry.apply(tesselator)
            mesh = tesselator.discretization
            offset = len(vertices)
            vertices.extend((p.x, p.y, p.z) for p in mesh.pointList)
            indices.extend([i + offset for i in index] for index in mesh.indexList)
            # one value per organ, repeated on all its vertices
            attribute.extend([values[shape.id]] * len(mesh.pointList))
        return (np.array(vertices, dtype=np.float32),
                np.array(indices, dtype=np.uint32),
                np.array(attribute, dtype=np.float32))

    @staticmethod
    def _k3d_output(plot, as_html, height, additional_js_code=""):
        if as_html:
            import html
            import warnings
            from IPython.display import HTML
            snapshot = plot.get_snapshot(additional_js_code=additional_js_code)
            with warnings.catch_warnings():
                warnings.simplefilter("ignore")  # IPython suggests IFrame, which needs a file or URL
                return HTML(f'<iframe srcdoc="{html.escape(snapshot)}" '
                            f'style="width: 100%; height: {height}px; border: none;"></iframe>')
        return plot
