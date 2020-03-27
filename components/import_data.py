import math
import pandas as pd
from datetime import datetime
import components.mongo_interface as mongo_interface
from pandas.io.json import json_normalize
from bson.objectid import ObjectId

def get_connection():
    return mongo_interface.get_connection()

def get_run_list():
    return mongo_interface.get_run_list()

def get_sample_component(sample_names, component_name):
    return mongo_interface.get_sample_component(sample_names, component_name)

def get_db_list():
    return mongo_interface.get_db_list()

def get_species_list(run_name=None):
    return mongo_interface.get_species_list(run_name)

def get_filtered_samples(specie):
    return mongo_interface.get_filtered_samples(specie)

def save_to_project(data_dict):
    if len(data_dict) > 1:
        for n in range(len(data_dict)):
            mongo_interface.save_to_project(data_dict[n])
    else:
        mongo_interface.save_to_project(data_dict[0])

def filter_all(species=None, species_source=None, group=None,
               qc_list=None, run_names=None, sample_ids=None,
               sample_names=None,
               pagination=None,
               projection=None):
    if sample_ids is None:
        query_result = mongo_interface.filter(
            run_names=run_names, species=species,
            species_source=species_source, group=group,
            qc_list=qc_list,
            sample_names=sample_names,
            pagination=pagination,
            projection=projection)
    else:
        query_result = mongo_interface.filter(
            samples=sample_ids, pagination=pagination,
            projection=projection)
    return pd.io.json.json_normalize(query_result)
