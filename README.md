# Introduction
These `jupyer` notebooks can be used to generate the figures in *The ubiquity of
directional and reciprocating motions in enzymes out of equilibrium* to be
published by Slochower and Gilson, 2017. There are two ways to interact with
this code: an interactive method and an automated method that can recreated the
published figures.

# Interactive method
Assuming dihedral histograms have already been computed and the directories have
been specified in `simulation.py`, it is easy to inspect the behavior of a
single (or a few) dihedrals. If the histograms are unavailable, see below for
instructions on how to generate them and set the paths.

For example:

```python
this = Simulation(data_source='adk_md_data')
this.name = 'chi2TYR103'
this.simulate()
plot_flux(this)
```

# Batch method


# 0. Run MD

# 1. Prepare dihedral histograms
- Insert `perl` script here. (This will require `cpptraj`)

# 2. Specify directories and parameters

# 3. Run code
- Add in directions to generate the summary dataframes.
