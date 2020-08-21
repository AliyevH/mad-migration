from datetime import datetime, date
from enum import Enum
import json


class DataTypeConvert:
    """
    This class will convert SqlAlchemy Data types to python objects
    We use this function to convert data in python level to be able to insert into database
    """
    def __init__(self, data, destination_type):
        """
        :param data: data
        :param destination_type: Type of column in destination database
        """
        self.data = data
        self.destination_type = destination_type

    def convert(self):
        """
        :return: Converted data in python level
        """
        return self.get_type_object(self.destination_type)(self.data)

    def get_type_object(self, data_type):
        """
        :param data_type: data type
        :return: object class
        """
        return {
            "varchar": str,
            "text": str,
            "nvarchar": str,
            "smallint": str,
            "char": str,

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



        }.get(data_type.lower())
