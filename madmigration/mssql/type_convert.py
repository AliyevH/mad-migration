from datetime import datetime, date
from time import time
from enum import Enum
import json
from uuid import UUID

def get_type_object(data_type):
    """
    :param data_type: data type
    :return: object class
    """
    return {
        "varchar": str,
        "char": str,
        "string": str,
        "text": str,
        "integer": int,
        "smallint": int,
        "bigint": int,
        "binary": bytes,
        "boolean": bool, 
        "bool": bool,  
        "bit": int,
        "date": date,
        "datetime": datetime,
        "timestamp": datetime,
        "time": datetime,
        "float": float,
        "real": float,
        "numeric": float,
        "money": float,
        "uuid": UUID,

    }.get(data_type.lower())
