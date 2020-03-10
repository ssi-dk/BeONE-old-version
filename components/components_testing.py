import components.import_data as import_data
from components import html_components as hc
import pymongo
import components.mongo_interface as mongo_interface
import os
from bson.objectid import ObjectId
KEY = "BIFROST_DB_KEY"
import pprint
import pandas as pd
CONNECTION = None

def get_connection():
    global CONNECTION
    if CONNECTION is not None:
        return CONNECTION
    else:
        mongo_db_key = os.getenv("BIFROST_DB_KEY", None)
        if mongo_db_key is None:
            exit("BIFROST_DB_KEY env variable is not set.")
        "Return mongodb connection"
        CONNECTION = pymongo.MongoClient(mongo_db_key)
        return CONNECTION


DB = "bifrost_prod"

connection = get_connection()
#collection_names = connection[DB].list_collection_names()
#dbs = connection.list_database_names()
db = connection[DB]

collection = db['samples']
#print(db.list_collection_names())

# runs = list(db.runs.find({},  # {"type": "routine"}, #Leave in routine
#                          {"name": 1,
#                           "_id": 0,
#                           "samples": 1}).sort([['metadata.created_at', pymongo.DESCENDING]]))
# run_options = [
#     {
#         "label": "{}".format(run["name"]),
#         "value": len(run["samples"])
#     } for run in runs]

run_list = import_data.get_run_list('bifrost_prod')
run_options = [
    {
        "label": "{}".format(run["name"]),
        "value": run["name"]
    } for run in run_list]

#df2 = pd.DataFrame(run_options)
#print(run_options)

sample_ids = mongo_interface.get_samples_id('200306_NB551234_0220_N_WGS_317_AH2M33AFX2', 'bifrost_prod')

#df = pd.DataFrame(sample_ids)
#print(sample_ids)
#sample_name = ["CPO20180130","DK_SSI_5080"]
#run_name = ['stefano_playground']

#samples = import_data.filter_all('bifrost_upgrade_test', run_names=['191115_NB551234_0191_N_WGS_283_AHVVLKAFXY'])
#test = pd.DataFrame(samples)
#query = list(collection.find({"properties.detected_species": "Clostridioides difficile"}))
projection = {"properties.detected_species": "Clostridioides difficile"}
#query2 = list(collection.find({"properties.detected_species": "Clostridioides difficile", "_id": ObjectId("5b957784954245218fec2c9a") }))
#query3 = list(collection.find({"_id": {"$in": sample_ids}, "$elemMatch": {"properties.detected_species": "Clostridioides difficile"} }))

#data = pd.DataFrame(query)
#print(data)

#species_options = mongo_interface.get_species_list(['200306_NB551234_0220_N_WGS_317_AH2M33AFX2','200304_NB551234_0219_N_WGS_316_AH2M7HAFX2'])

#print(species_options)

# test = species_list[:2]
# print(test)
#
#
# for i in range(2):
#     print(test[i]['count'])
#
# species_options = [
#     {"label": "{}".format(i['_id']),
#      "value": "{}".format(i['count'])} for i in test]
#
# print(species_options)

#print(species_options)

#print(species_list)

test = db.samples.find_one()
#print(test)
#pipeline = [{"$unwind": "$name"}, {"$group": {"_id": "$name", "count": {"$sum": 1}}}]
# pipeline = [{"$group": {"_id": "$properties.detected_species", "count": {"$sum": 1}}},
#             {"$sort": {"_id": 1}}]


#species = list(db.samples.aggregate(pipeline))
# species = list(db.samples.aggregate([
#     {
#         {
#             "$unwind:" "$properties.detected_species"
#         }
#     },
#     {
#         "$sort": {"_id": 1}
#     }
# ]))
#print(species)

#run_name = ['200306_NB551234_0220_N_WGS_317_AH2M33AFX2','200304_NB551234_0219_N_WGS_316_AH2M7HAFX2','200228_NB551234_0218_N_WGS_315_AH2LT2AFX2']
run_name = ['200228_NB551234_0218_N_WGS_315_AH2LT2AFX2']

#species_list = mongo_interface.get_species_list(run_name)
#print(species_list)
#print(len(species_list))

samples = mongo_interface.filter(species=['Campylobacter jejuni'])
print(len(samples))
