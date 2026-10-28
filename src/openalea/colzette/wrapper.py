import sys, os
import pandas as pd
import numpy as np
from dataclasses import dataclass, field, fields

from pathlib import Path

from openalea.colzette.colzette import compute_thermal_time, get_params_intercrop
from openalea.colzette.simulation import run_static_simulation, run_static_mixture_simulation
from openalea.colzette.data import data_dir


def parameter(value, description: str, genre: str, min_value: float = None, max_value: float = None):
    return field(default=value, metadata=dict(
        description=description, genre=genre, min_value=min_value, max_value=max_value,
        variable_type="parameter"
    ))

SCENARIOS = {
    "mono_brassica": {
        "species_brassica": "Rapeseed",
        "species_legume": None,
        "Type_simul": "monocrop_vigo",
        "sowing_option": "rows"
    },

    "mono_legume": {
        "species_brassica": None,
        "species_legume": "Fababean",
        "Type_simul": "monocrop_vigo",
        "sowing_option": "rows"
    },

    "intercrop": {
        "species_brassica": "Rapeseed",
        "species_legume": "Fababean",
        "Type_simul": "intercrop_vigo",
        "sowing_option": "rows"
    }
}


@dataclass
class Colzette:
    # Hardcoded simulation hyperparameters which will not be played with during sensitivity analyses
    Type_simul: str = "monocrop_vigo"

    specie_brassica: str = "Rapeseed"

    type_brassica: str = "intercrop_aviso_RRF"

    specie_legume: str = None

    type_legume: str = None

    stand_option: str = 'plot'

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
            brassica_parameters = [p for p in self.parameters() if p.metadata["genre"] == "brassica"]
            for p in brassica_parameters:
                genre = p.metadata["genre"]
                p_name = p.name[:p.name.find(genre)-1]
                self.dict_params[self.specie_brassica][p_name] = p.default
        
        if self.specie_legume is not None:
            legume_parameters = [p for p in self.parameters() if p.metadata["genre"] == "legume"]
            for p in legume_parameters:
                genre = p.metadata["genre"]
                p_name = p.name[:p.name.find(genre)-1]
                self.dict_params[self.specie_legume][p_name] = p.default

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
            lambda self: self.climatic_inputs["PAR"].iloc[self.day_index] * 100
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

    def run(self, *args, **kwds):
        while self.day_index < self.simulation_length:
            self.__call__()
            self.log()
            self.day_index += 1


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
    def parameters(cls):
        fds = [f for f in fields(cls) if len(f.metadata) > 0]
        return [f for f in fds if f.metadata["variable_type"] == "parameter"]
    
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
