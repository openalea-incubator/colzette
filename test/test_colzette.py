import pytest

from openalea.colzette.colzette_lib import get_nb_leaflets

def test_get_nb_leaflets():

    n = get_nb_leaflets(10)
    assert n == 5
