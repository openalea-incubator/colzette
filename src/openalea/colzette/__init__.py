"""**colzette**

A Parametric Model for oilseed rape and legume
"""

from importlib.metadata import version, PackageNotFoundError

try:
    __version__ = version("openalea.colzette")
except PackageNotFoundError:
    # package is not installed
    pass
