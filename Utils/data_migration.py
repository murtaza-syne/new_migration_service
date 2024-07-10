import redis
from configs.databse import collection_name
import json

# Connect to Redis
bgbuilder_redis = redis.Redis(
    host="carbgbuilder-001.gmaq4a.0001.use1.cache.amazonaws.com",
    port=6379,
    db=0,
    decode_responses=True,
)

for key in bgbuilder_redis.scan_iter('*'):
    value = bgbuilder_redis.get(key)
    value_dict = json.loads(value.decode('utf-8'))  # Assuming the value is a JSON string
    value_dict['_id'] = key.decode('utf-8')
    value_dict["is_active"] = True
    value_dict["version_number"] = 1
    collection_name.insert_one(value_dict)

print("Data migration completed.")
