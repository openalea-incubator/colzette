# Installation


Conda must be installed, please follow the instructions and recommendations [here](https://openalea.readthedocs.io/en/latest/install.html).

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
mamba env create -f conda/environment.yml
mamba activate colzette_dev

# (Optional) Test your installation
cd test; pytest
```
This will create a conda environment with dependencies installed and install colzette in editable state.

## Running notebook Examples

you can run the jupyter notebook in `doc/examples`.
First install `jupyterlab` and `òpenalea.widgets`
```bash
mamba install -c openalea3 -c conda-forge jupyterlab openalea.widgets
```

then in `doc/examples` launch jupyter-lab
````bash
cd doc/examples
jupyter-lab
````
