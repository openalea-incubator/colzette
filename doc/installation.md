# Installation

You must use conda environment : <https://docs.conda.io/en/latest/index.html>

## Users

### Create a new environment with colzette installed in there

```bash

mamba create -n colzette -c openalea3 -c conda-forge  openalea.colzette
mamba activate colzette
```

Install colzette in a existing environment

```bash
mamba install -c openalea3 -c conda-forge openalea.colzette
```

### (Optional) Test your installation

```bash
mamba install -c conda-forge pytest
git clone https://github.com/openalea/colzette.git
cd colzette/test; pytest
```

## Developers

### Install From source

```bash
# Install dependency with conda
mamba env create -n phm -f conda/environment.yml
mamba activate colzette

# Clone colzette and install
git clone https://github.com/openalea/colzette.git
cd colzette
pip install .

# (Optional) Test your installation
cd test; pytest
```
