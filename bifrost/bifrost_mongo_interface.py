import pymongo
import os
from datetime import datetime
import math
import re
import pymongo
import keys  # .gitgnored file
from bson.objectid import ObjectId
from bson.son import SON
import atexit
import math

CONNECTION = None

PAGESIZE = 10


def date_now():
    """
    Needed to keep the same date in python and mongo, as mongo rounds to millisecond
    """
    d = datetime.utcnow()
    return d.replace(microsecond=math.floor(d.microsecond/1000)*1000)

CONNECTION = None


def close_connection():
    global CONNECTION
    if CONNECTION is not None:
        CONNECTION.close()

atexit.register(close_connection)

def get_connection():
    global CONNECTION
    if CONNECTION is not None:
        return CONNECTION
    else:
        mongo_db_key = os.getenv("LOCAL_DB_KEY", None)
        if mongo_db_key is None:
            exit("LOCAL_DB_KEY env variable is not set.")
        "Return mongodb connection"
        CONNECTION = pymongo.MongoClient(mongo_db_key)
        return CONNECTION

def check_run_name(name):
    connection = get_connection()
    db = connection.get_database()
    # Fastest.
    run = db.runs.find({"name": name}).limit(1).count(True)
    return run is not 0

def get_run_list():
    connection = get_connection()
    db = connection['bifrost_upgrade_test']
    # Fastest.
    runs = list(db.runs.find( {},#{"type": "routine"}, #Leave in routine
                                {"name": 1,
                                "_id": 0,
                                "samples": 1}).sort([['metadata.created_at', pymongo.DESCENDING]]))
    return runs

def get_group_list(run_name=None):
    connection = get_connection()
    db = connection.get_database()
    if run_name is not None:
        run = db.runs.find_one(
            {"name": run_name},
            {
                "_id": 0,
                "samples._id": 1
            }
        )
        if run is None:
            run_samples = []
        else:
            run_samples = run["samples"]
        sample_ids = [s["_id"] for s in run_samples]
        groups = list(db.samples.aggregate([
            {
                "$match": {
                    "_id": {"$in": sample_ids},
                }
            },
            {
                "$group": {
                    "_id": "$properties.sample_info.summary.group",
                    "count": {"$sum": 1}
                }
            }
        ]))
    else:
        groups = list(db.samples.aggregate([
            {
                "$group": {
                    "_id": "$properties.sample_info.summary.group",
                    "count": { "$sum":1 }
                }
            }
        ]))

    return groups


def get_species_list(species_source, run_name=None):
    connection = get_connection()
    db = connection.get_database()
    if species_source == "provided":
        spe_field = "properties.sample_info.summary.provided_species"
    else:
        spe_field = "properties.species_detection.summary.detected_species"
    if run_name is not None:
        run = db.runs.find_one(
            {"name": run_name},
            {
                "_id": 0,
                "samples._id": 1
            }
        )
        if run is None:
            run_samples = []
        else:
            run_samples = run["samples"]
        sample_ids = [s["_id"] for s in run_samples]
        species = list(db.samples.aggregate([
            {
                "$match": {
                    "_id": {"$in": sample_ids}
                }
            },
            {
                "$group": {
                    "_id": "$" + spe_field,
                    "count": {"$sum": 1}
                }
            },
            {
                "$sort": {"_id": 1}
            }
        ]))
    else:
        species = list(db.samples.aggregate([
            {
                "$group": {
                    "_id": "$" + spe_field,
                    "count": {"$sum": 1}
                }
            },
            {
                "$sort": {"_id": 1}
            }
        ]))
    return species


def filter_qc(qc_list):
    if qc_list is None or len(qc_list) == 0:
        return None
    qc_query = []
    for elem in qc_list:
        if elem == "Not checked":
            qc_query.append({"$and": [
                {"properties.datafiles.summary.paired_reads": {"$exists": True}},
                {"properties.stamper.summary.stamp.value": {"$exists": False}}
            ]})
        elif elem == "core facility":
            qc_query.append({"$or": [
                        {"properties.datafiles.summary.paired_reads": {"$exists": False}},
                        {"properties.stamper.summary.stamp.value": "core facility"}
                    ]
                })
        else:
            qc_query.append({"properties.stamper.summary.stamp.value": elem})
    return {"$match": {"$and": qc_query}}


def filter(run_names=None,
           species=None, species_source="species", group=None,
           qc_list=None, samples=None, pagination=None,
           sample_names=None,
           projection=None):
    if species_source == "provided":
        spe_field = "properties.provided_species"
    elif species_source == "detected":
        spe_field = "properties.detected_species"
    else:
        spe_field = "properties.species"
    connection = get_connection()
    db = connection['bifrost_upgrade_test']
    query = []
    sample_set = set()
    if sample_names is not None and len(sample_names) != 0:
        sample_names_query = []
        for s_n in sample_names:
            if s_n.startswith("/") and s_n.endswith("/"):
                sample_names_query.append(re.compile(s_n[1:-1]))
            else:
                sample_names_query.append(s_n)
        query.append({"name": {"$in": sample_names_query}})
    if samples is not None and len(samples) != 0:
        sample_set = {ObjectId(id) for id in samples}
        query.append({"_id": {"$in": list(sample_set)}})
    if run_names is not None and len(run_names) != 0:
        runs = list(db.runs.find(
            {"name": {"$in": run_names}},
            {
                "_id": 0,
                "samples._id": 1
            }
        ))
        if runs is None:
            run_sample_set = set()
        else:
            run_sample_set = {s["_id"] for run in runs for s in run['samples']}

        if len(sample_set):
            inter = run_sample_set.intersect(sample_set)
            query.append({"_id": {"$in": list(inter)}})
        else:
            query.append({"_id": {"$in": list(run_sample_set)}})
    if species is not None and len(species) != 0:


        if "Not classified" in species:
            query.append({"$or":
                [
                    {spe_field: None},
                    {spe_field: {"$in": species}},
                    {spe_field: {"$exists": False}}
                ]
            })
        else:
            query.append({spe_field: {"$in": species}})
    if group is not None and len(group) != 0:
        if "Not defined" in group:
            query.append({"$or":
                [
                    {"properties.sample_info.summary.group": None},
                    {"properties.sample_info.summary.group": {"$in": group}},
                    {"properties.sample_info.summary.group": {"$exists": False}}
                ]
            })
        else:
            query.append(
                {"properties.sample_info.summary.group": {"$in": group}})

    if pagination is not None:
        p_limit = pagination['page_size']
        p_skip = pagination['page_size'] * pagination['current_page']
    else:
        p_limit = 1000
        p_skip = 0

    skip_limit_steps = [
        {"$skip": p_skip}, {"$limit": p_limit}
    ]

    qc_query = filter_qc(qc_list)

    if len(query) == 0:
        if qc_query is None:
            match_query = {}
        else:
            match_query = qc_query["$match"]
    else:
        if qc_query is None:
            match_query = {"$and": query}
        else:
            match_query = {"$and": query + qc_query["$match"]["$and"]}
    query_result = list(db.samples.find(
        match_query, projection).sort([('name', pymongo.ASCENDING)]).skip(p_skip).limit(p_limit))

    return query_result

def get_species_QC_values(ncbi_species):
    connection = get_connection()
    db = connection.get_database('bifrost_species')
    species = db.species.find_one({"ncbi_species": ncbi_species}, {
                        "min_length": 1, "max_length": 1})
    if species is not None:
        return species
    species = db.species.find_one({"organism": ncbi_species}, {
        "min_length": 1, "max_length": 1})
    if species is not None:
        return species
    species = db.species.find_one({"group": ncbi_species}, {
        "min_length": 1, "max_length": 1})
    if species is not None:
        return species
    species = db.species.find_one({"organism": "default"}, {
        "min_length": 1, "max_length": 1})
    return species

