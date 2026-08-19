
from openalea.colzette.colzette import get_nb_leaflets_fababean

def test_get_nb_leaflets_fababean():

    n = get_nb_leaflets_fababean(10)
    assert n == 5
