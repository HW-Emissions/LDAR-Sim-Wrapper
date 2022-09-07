# ------------------------------------------------------------------------------
# Program:     The LDAR Simulator (LDAR-Sim)
# File:        LDAR-Sim main
# Purpose:     Interface for parameterizing and running LDAR-Sim.
#
# Copyright (C) 2018-2021  Intelligent Methane Monitoring and Management System (IM3S) Group
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the MIT License as published
# by the Free Software Foundation, version 3.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# MIT License for more details.

# You should have received a copy of the MIT License
# along with this program.  If not, see <https://opensource.org/licenses/MIT>.
#
# ------------------------------------------------------------------------------
import datetime
import multiprocessing as mp
import os
import pickle
import shutil
import json
import sys
import yaml
from pandas import read_csv
from pathlib import Path
from processing.timeseries import process as ts_process
from processing.leaks import process as leaks_process
from processing.sites import process as sites_process
# Get directories and set up root
wrap_dir = Path(os.path.dirname(__file__))
root_dir = wrap_dir / 'LDAR_Sim/LDAR_Sim'
src_dir = root_dir / 'src'
os.chdir(root_dir)
# Add the source directory to the import file path to import all
# LDAR-Sim modules
sys.path.insert(1, str(src_dir))

if __name__ == '__main__':
    from initialization.args import files_from_args, get_abs_path
    from initialization.input_manager import InputManager, NoAliasDumper
    from initialization.sims import create_sims
    from initialization.sites import init_generator_files
    from ldar_sim_run import ldar_sim_run
    from utils.generic_functions import check_ERA5_file
    # Get route directory , which is parent folder of ldar_sim_main file
    # Set current working directory directory to root directory

    # --- Retrieve input parameters and parse ---
    parameter_filenames = files_from_args(wrap_dir)
    input_manager = InputManager()
    sim_params = input_manager.read_and_validate_parameters(
        parameter_filenames)

    # --- Clear cache ---
    cache_dir_parent = wrap_dir / ".cache"
    if not os.path.exists(cache_dir_parent):
        os.makedirs(cache_dir_parent)

    cache_dir = cache_dir_parent / sim_params['program_set_name']
    if os.path.exists(cache_dir):
        shutil.rmtree(cache_dir)
    os.makedirs(cache_dir)

    # --- Assign local variabls
    ref_program = sim_params['reference_program']
    base_program = sim_params['baseline_program']
    in_dir = get_abs_path(sim_params['input_directory'], wrap_dir)
    out_dir = get_abs_path(sim_params['output_directory'], wrap_dir)
    programs = sim_params.pop('programs')
    # --- Run Checks ----
    check_ERA5_file(in_dir, programs)
    has_ref = ref_program in programs
    has_base = base_program in programs

    # --- Setup Output folder
    if os.path.exists(out_dir):
        shutil.rmtree(out_dir)
    os.makedirs(out_dir)

    # merging subtype file with global parameters to dump
    if programs[sim_params['baseline_program']]['subtype_file']:
        subtype_added_dict = {**{'globals': sim_params}, **{'subtype': read_csv(
            in_dir/programs[sim_params['baseline_program']]['subtype_file']).to_dict()}}
    else:
        with open(cache_dir / 'params.yaml', 'w') as f:
            subtype_added_dict = {
                **{'globals': sim_params}, **{'subtype': None}}
    # Combine all parameters into a single dictionary for a single output
    added_programs = {**subtype_added_dict, **{'programs': programs}}

    with open(cache_dir / 'params.yaml', 'w') as f:
        f.write(yaml.dump(added_programs, Dumper=NoAliasDumper))

    input_manager.write_parameters(out_dir / 'parameters.yaml')

    # If leak generator is used and there are generated files, user is prompted
    # to use files, If they say no, the files will be removed
    if sim_params['pregenerate_leaks']:
        generator_dir = in_dir / "generator"
        init_generator_files(
            generator_dir, input_manager.simulation_parameters, in_dir, programs[base_program])

    # --- Create simulations ---
    simulations = create_sims(sim_params, programs,
                              generator_dir, in_dir, out_dir, input_manager)

    # --- Run simulations (in parallel) --
    with mp.Pool(processes=sim_params['n_processes']) as p:
        sim_outputs = p.starmap(ldar_sim_run, simulations)
    print("Done runing simulations...")
    print("Processing outputs...")
    # --- Process Outputs ---
    prog_leaks = leaks_process(
        sim_outputs, cache_dir, sim_params['baseline_program'])
    prog_ts = ts_process(sim_outputs, sim_params, cache_dir)
    prog_sites = sites_process(sim_outputs, cache_dir)
    json.dump(prog_sites.to_json(), open(cache_dir / "sites.json", "w"))

    meta = {
        'n_sites': len(sim_outputs[0]['sites']),
        'n_days': len(sim_outputs[0]['timeseries']),
        'n_leaks': len(sim_outputs[0]['leaks']),
        'pregen_leaks': sim_params['pregenerate_leaks'],
        'reference_program': sim_params['reference_program'],
        'baseline_program': sim_params['baseline_program']}
    pickle.dump(meta, open(cache_dir / "meta.p", "wb"))

    # Write program metadata
    metadata = open(out_dir / '_metadata.txt', 'w')
    metadata.write(str(programs) + '\n' +
                   str(datetime.datetime.now()))

    metadata.close()
