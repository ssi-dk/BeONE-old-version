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

def get_db_list():
    return mongo_interface.get_db_list()

def get_species_list(species_source, run_name=None):
    return mongo_interface.get_species_list(species_source, run_name)