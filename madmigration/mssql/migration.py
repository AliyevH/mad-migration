from sqlalchemy.ext.mutable import MutableDict
from sqlalchemy.dialects.mssql import (
    BIGINT,
    BINARY,
    BIT,
    CHAR,
    DATE,
    DATETIME,
    DATETIME2,
    DATETIMEOFFSET,
    DECIMAL,
    FLOAT,
    IMAGE,
    INTEGER,
    MONEY,
    NCHAR,
    NTEXT,
    NUMERIC,
    NVARCHAR,
    REAL,
    SMALLDATETIME,
    SMALLINT,
    SMALLMONEY,
    TEXT,
    TIME,
    TIMESTAMP,
    TINYINT,
    UNIQUEIDENTIFIER,
    VARBINARY,
    VARCHAR,
)
from sqlalchemy import DateTime
from sqlalchemy_utils import UUIDType
from madmigration.basemigration.base import BaseMigrate
from madmigration.config.conf import Config
from pprint import pprint

#TODO for fk keys RESTRICT|CASCADE|SET NULL|NO ACTION|SET DEFAULT

class MssqlMigrate(BaseMigrate):
    def __init__(self, config: Config, destination_db):
        super().__init__(config, destination_db)
        self.collect_table_names()

    @staticmethod
    def get_column_type(type_name: str) -> object:
        """Get class of db type
        :param type_name: str
        :return: object class
        """
        return {
            "varchar": VARCHAR,
            "char": CHAR,
            "string": VARCHAR,
            "text": TEXT,
            "integer": INTEGER,
            "smallint": SMALLINT,
            "bigint": BIGINT,
            "binary": BINARY,
            "boolean": BIT, #FIXME  raise error when insert bool value
            "bool": BIT,   #FIXME  raise error when insert bool value
            "bit": BIT,
            "date": DATE,
            "datetime": DATETIME,
            "timestamp": TIMESTAMP,
            "time": TIME,
            "float": FLOAT,
            "real": REAL,
            # "array": ARRAY, #FIXME column with array include array elemet type argument
            "numeric": NUMERIC,
            "money": MONEY,
            "uuid": UUIDType(binary=False),
        }.get(type_name.lower())

