



from datetime import datetime, date
from uuid import UUID

def get_type_object(data_type):
    """
    :param data_type: data type
    :return: object class
    """
    
    return {

        "string": str,
        "str": str,
        "varchar": str,
        "text": str,
        "nvarchar": str,
        "char": str,
        "character": str,
        "varying": str,
        "composite": str,

        "int": int,
        "integer": int,
        "bigint": int,
        "numeric": int,
        "smallint": int,

        "boolean": bool,
        "bool": bool,

        "float": float,
        "numeric": float,
        "decimal": float,
        "double": float,
        "precision": float,
        "real": float,
        "serial": float,
        "arbitrary": float,

        "date": date,
        "datetime": datetime.fromisoformat,
     
        # "timestamp": timestamp,

      
        "uuid": UUID,

        "binary": bytes,


     

    }.get(data_type.lower())
