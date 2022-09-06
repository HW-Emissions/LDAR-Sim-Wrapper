from processing.outputs import clean_sim_df

def process(sim_outputs, CACHE_DIR):
    prog_sites = clean_sim_df(sim_outputs, 'sites', index='facility_ID', params=[
        {'in': 'facility_ID', 'out': 'facility_ID', 'type': str},
        {'in': 'lat', 'out': 'lat', 'type': float},
        {'in': 'lon', 'out': 'lon', 'type': float},
        {'in': 'total_emissions_kg', 'out': 'total_emissions_kg', 'type': float},
        {'in': 'subtype_code', 'out': 'subtype_code', 'type': str},
    ], aggregate=False)

    return prog_sites
