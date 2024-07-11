from fastapi.encoders import jsonable_encoder
from bson import ObjectId
from datetime import datetime
from enum import Enum

def custom_jsonable_encoder(data):
    if isinstance(data, dict):
        return {k: custom_jsonable_encoder(v) for k, v in data.items()}
    elif isinstance(data, list):
        return [custom_jsonable_encoder(i) for i in data]
    elif isinstance(data, ObjectId):
        return str(data)
    elif isinstance(data, Enum):
         return data.value
    elif isinstance(data,datetime):
        return data
    else:
        return jsonable_encoder(data)