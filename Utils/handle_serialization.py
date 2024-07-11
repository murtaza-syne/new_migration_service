from datetime import datetime
from bson import ObjectId

from enum import Enum

def convert_for_serialization(data_dict):
    
    for key, value in data_dict.items():
        if isinstance(value, Enum):
            data_dict[key] = value.value
        elif isinstance(value, datetime):
            data_dict[key] = value.isoformat()
        elif isinstance(value, ObjectId):
            data_dict[key] = str(value)
    return data_dict
