# LDAR-Sim-Wrapper

Wrapper for LDAR-Sim - Generates outputs for the LDAR-Sim Drag and Drop dashboard.

## About LDAR-Sim

The Leak Detection and Repair Simulator (LDAR-Sim) is an open-source modeling framework for exploring the effectiveness of methane leak detection programs. The purpose of LDAR-Sim is to enable transparent, collaborative, flexible, and intuitive investigation of emerging LDAR technologies, methods, work practices, regulations, and deployment strategies.

LDAR-Sim has many potential uses, including:

  1) Test emissions reduction equivalence among distinct LDAR programs
  2) Evaluate performance and cost of methane sensing technologies and work practices
  3) Predict the emissions mitigation of proposed or existing fugitive methane policies
  4) Inform the development and niche of technologies and work practices

To learn more about LDAR-Sim, you can:

  1) User manual [manual](USER_MANUAL.md)
  2) Read our [story map](https://arcg.is/1rXeX10) (less technical introduction).
  3) Read [Fox et al., 2020](https://www.sciencedirect.com/science/article/pii/S0959652620352811).

For first time users, we recommend attempting to reproduce the case study results in Fox et al. 2020 (see below).

Thomas Fox: thomas@highwoodemissions.com

Mozhou Gao: mozhou.gao@ucalgary.ca

Thomas Barchyn: tbarchyn@ucalgary.ca

Chris Hugenholtz: chhugenh@ucalgary.ca

## LDAR-Sim Licensing and Use

LDAR-Sim was invented by Thomas Fox, Mozhou Gao, Thomas Barchyn, and Chris Hugenholtz at the University of Calgary's Centre for Smart Emissions Sensing Technologies.

LDAR-Sim is free software: you can redistribute it and/or modify it under the terms of the MIT License . LDAR-Sim is distributed in the hope that it will be useful, but without any warranty; without even the implied warranty of merchantability or fitness for a particular purpose.

NOTE: This applies to all versions following Commit 69c27ec, Made on March 1st, 2021, Previous versions of LDAR-Sim were licensed under the GNU Affero General Public License. All redistributions or modifications made on LDAR-Sim versions created before Commit 69c27ec (March 1st, 2021) are required to be in compliance with version 3 of the GNU Affero General Public License.

## [Fox_etal_2020 Release](https://github.com/tarcadius/LDAR_Sim/tree/Fox_etal_2020)

The Fox et al. 2020 release is immortalized in a separate branch that can be found by [clicking here](https://github.com/tarcadius/LDAR_Sim/tree/Fox_etal_2020).

The Fox et al., 2020 release contains the exact code and inputs used in [our LDAR-Sim synthesis paper](https://www.sciencedirect.com/science/article/pii/S0959652620352811). We recommend using this release, especially for first time users.

Citation for this release: Fox, Thomas A., Mozhou Gao, Thomas E. Barchyn, Yorwearth L. Jamin, and Chris H. Hugenholtz. "An agent-based model for estimating emissions reduction equivalence among leak detection and repair programs." Journal of Cleaner Production (2020): 125237.

## Step 1: Before you begin

Read and understand the LDAR-Sim LICENSE (MIT License).
Read the user manual [manual](USER_MANUAL.md)
Read [Fox et al 2020](https://www.sciencedirect.com/science/article/pii/S0959652620352811) to familiarize yourself with LDAR-Sim fundamentals.

## Step 2: Installing Packages with Conda

Using Conda (Conda-forge) and the requirements file included in the "install folder" Follow the directions included in the Setting Up LDAR Sim Dev Environment file. The requirements.txt file can also be used with PIP and pipenv, but Python should be installed seperately.

- Install Miniconda3 newest version
- From Conda Shell: cd into LDAR-Sim-Wrapper/install

  `conda config --add channels conda-forge`

  `conda config --set channel_priority strict1`

  `conda create -n ldar_sim --file requirements.txt`

  `conda activate ldar_sim`

Alternatively pip and pipenv can be used to install there requirements file with:

  `pip install ldar_sim -r requirements.txt`

## Running the Sim

To organize multiple cache files, you can create folders within the sims folder for each set of sims.

To run:

    python -m main -P ./sims/[foldername]

## Parameter specific to the Wrapper

### program_set_name

Program set name determines the name of the output folder created in the .cache folder. To use the wrapper to run LDAR-Sim, program set name must be present in the global parameter file.
