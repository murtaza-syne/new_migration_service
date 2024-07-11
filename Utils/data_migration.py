import redis
from configs.databse import current_collection_name
import json
import datetime


bgbuilder_redis = redis.Redis(
    host="carbgbuilder-001.gmaq4a.0001.use1.cache.amazonaws.com",
    port=6379,
    db=0,
    decode_responses=True,
)


def run_migration():
    for key in bgbuilder_redis.scan_iter('*'):
        value = bgbuilder_redis.get(key)
        value = json.loads(value)
        value["is_active"] = True
        value["version_number"] = 1

        if value.get("created_time"):
            value['created_time'] = datetime.datetime.fromtimestamp(value['created_time'])
        if value.get("last_modified_time"):
            value['last_modified_time'] = datetime.datetime.fromtimestamp(value['last_modified_time'])
        current_collection_name.insert_one(value)

    
    print("Data migration completed.")





