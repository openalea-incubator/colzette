import os
import sys

import pandas as pd
import pytest

# CARIBU runs its ray tracing executables (periodise, s2v, canestrad...) through the PATH, which only contains the
# environment folders when it is activated: add them so that tests also run from a non activated interpreter.
os.environ["PATH"] = os.pathsep.join(
    [os.path.join(sys.prefix, "Scripts"), os.path.join(sys.prefix, "Library", "bin"), os.path.join(sys.prefix, "bin"),
     os.environ["PATH"]])

from openalea.colzette import Colzette, scenario_intercrop_brassica_faba, scenario_monocrop_brassica
from openalea.colzette.colzette import get_params_intercrop
from openalea.colzette.data import data_dir

# DAS 4: no leaf area yet, DAS 40 and 80: rapeseed and fababean both have leaves
NO_LEAF_DAY = 4
LEAF_DAYS = [40, 80]


def read_params(specie):
    return pd.read_csv(data_dir / "parameters" / f"type_params_{specie.lower()}.csv", sep="\t")


@pytest.fixture(scope="session")
def params_file():
    """Default parameter file of a species, as read by the wrapper"""
    return read_params


@pytest.fixture(scope="session")
def no_leaf_day():
    return NO_LEAF_DAY


@pytest.fixture(scope="session")
def leaf_days():
    return LEAF_DAYS


@pytest.fixture(scope="session")
def params_rapeseed():
    return get_params_intercrop("Rapeseed", None, read_params("Rapeseed"), pd.DataFrame(), "One simulation")["Rapeseed"]


@pytest.fixture(scope="session")
def params_fababean():
    return get_params_intercrop(None, "Fababean", pd.DataFrame(), read_params("Fababean"), "One simulation")["Fababean"]


# Simulations are shared between tests: each simulated day takes a few seconds

@pytest.fixture(scope="session")
def monocrop():
    c = Colzette(**scenario_monocrop_brassica)
    c.run([NO_LEAF_DAY] + LEAF_DAYS)
    return c


@pytest.fixture(scope="session")
def intercrop():
    c = Colzette(**scenario_intercrop_brassica_faba)
    c.run(LEAF_DAYS)
    return c
