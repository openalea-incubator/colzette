# colzette

_________________

[![Docs](https://readthedocs.org/projects/colzette/badge/?version=latest)](https://colzette.readthedocs.io/)
[![Build Status](https://github.com/openalea-incubator/colzette/actions/workflows/openalea_ci.yml/badge.svg)](https://github.com/openalea-incubator/colzette/actions/workflows/openalea_ci.yml)
[![Python Version](https://img.shields.io/badge/python-3.10%20%7C%203.11%20%7C%203.12%20%7C%203.13-blue)](https://www.python.org/downloads/)
[![Anaconda-Server Badge](https://anaconda.org/openalea3/openalea.colzette/badges/version.svg)](https://anaconda.org/openalea3/openalea.colzette)
[![License](https://img.shields.io/badge/License--CeCILL-C-blue)](https://www.cecill.info/licences/Licence_CeCILL-C_V1-en.html)
[![Binder](https://mybinder.org/badge_logo.svg)](https://mybinder.org/v2/gh/openalea-incubator/colzette.git/HEAD?urlpath=%2Fdoc%2Ftree%2Fdoc%2Fexamples%2Findex.ipynb)
_________________

**colzette** A Parametric Model for oilseed rape and legume.

### Status

Python package

### License

CecILL-C

### Installation

First, **Conda** needs to be installed. It is a package manager that can be installed on Linux, Windows, and Mac. we recommand to install [miniforge](https://github.com/conda-forge/miniforge).

#### for user
Creating a new conda environment with colzette and its dependencies installed
```bash
mamba create -n colzette -c openalea3/label/dev -c openalea3 -c conda-forge openalea.colzette
```

#### for developer
```bash
mamba env create -f ./conda/environment.yml
```
This will create a conda environment with dependencies installed and install colzette in editable state.

### Contributors

Thanks to all that contribute making this package what it is !

<a href="https://github.com/openalea-incubator/colzette/graphs/contributors">
  <img src="https://contrib.rocks/image?repo=openalea-incubator/colzette" />
</a>
