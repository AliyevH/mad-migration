from datetime import datetime, date
from enum import Enum
import json
from uuid import uuid4

def get_type_object(data_type):
    """
    :param data_type: data type
    :return: object class
    """
    return {
        "uuid": uuid4,
        "str": str,
        "varchar": str,
        "text": str,
        "nvarchar": str,
        "smallint": str,
        "char": str,

        "int": int,
        "integer": int,
        "bigint": int,

        "float": float,
        "numeric": float,
        "decimal": float,

        "date": date,
        "datetime": datetime,

        "binary": bytes,
        "enum": Enum,
        "set": set,

        "json": dict,

        "boolean": bool,
        "bool": bool,
        None: None

    }.get(data_type.lower())
