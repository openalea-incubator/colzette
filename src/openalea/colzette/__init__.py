"""**colzette**

A Parametric Model for oilseed rape and legume
"""

from importlib.metadata import version, PackageNotFoundError
from openalea.colzette.wrapper import Colzette, scenario_monocrop_brassica, scenario_intercrop_brassica_faba

try:
    __version__ = version("openalea.colzette")
except PackageNotFoundError:
    # package is not installed
    pass
