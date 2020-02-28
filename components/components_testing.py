import components.import_data as import_data
from components import html_components as hc
import pymongo
import components.mongo_interface as mongo_interface
import os
from bson.objectid import ObjectId
KEY = "BIFROST_DB_KEY"
import pandas as pd
import dash_table
import pprint

def get_connection(KEY):
    if KEY is None:
        KEY = "LOCAL_DB_KEY"

    mongo_db_key = os.getenv(KEY, None)
    if mongo_db_key is None:
        exit("BIFROST_DB_KEY env variable is not set.")
    "Return mongodb connection"
    CONNECTION = pymongo.MongoClient(mongo_db_key)
    return CONNECTION

DB = "bifrost_prod"

connection = get_connection(KEY)
#collection_names = connection[DB].list_collection_names()
dbs = connection.list_database_names()

#print(dbs)
db = connection[DB]

coll = db['runs']

runs = list(db.runs.find({},  # {"type": "routine"}, #Leave in routine
                         {"name": 1,
                          "_id": 0,
                          "samples": 1}).sort([['metadata.created_at', pymongo.DESCENDING]]))
run_options = [
    {
        "label": "{}".format(run["name"]),
        "value": len(run["samples"])
    } for run in runs]

df2 = pd.DataFrame(run_options)

sample_ids = mongo_interface.get_samples_id("not defined")

df = pd.DataFrame(sample_ids)
print(df)

samples = import_data.filter_all(
    sample_ids=sample_ids)

test = pd.DataFrame(samples)

for col in test.columns:
    print(col)

#print(test['properties.mlst.summary.strain'])
#print(test.loc[test['properties.species_detection.summary.detected_species'] == 'Escherichia coli'][["_id", 'properties.mlst.summary.strain', 'name']])

#print(df)

# test = list(db.sample_components.find({
#         "sample._id": {"$in": list(map(lambda x: ObjectId(x), sample_ids))},
#         "component.name": "whats_my_species"
#     }, {"path": 1, "sample": 1}))
#
# print(test)
#samples = import_data.filter_all(sample_ids=sample_ids)
#samples = hc.generate_table(samples)
#print(samples)

