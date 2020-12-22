from sqlalchemy.ext.mutable import MutableDict
from sqlalchemy.dialects.postgresql import (
    ARRAY,
    BIGINT,
    BIT,
    BOOLEAN,
    BYTEA,
    CHAR,
    DATE,
    # DOUBLE_PRECISION,
    # ENUM,
    FLOAT,
    INET,
    INTEGER,
    # INTERVAL,
    JSON,
    JSONB,
    MACADDR,
    MONEY,
    NUMERIC,
    OID,
    REAL,
    SMALLINT,
    TEXT,
    TIME,
    TIMESTAMP,
    VARCHAR,
)
from sqlalchemy import DateTime
from sqlalchemy_utils import UUIDType
from madmigration.basemigration.base import BaseMigrate
from madmigration.config.conf import Config
from pprint import pprint


class PgMigrate(BaseMigrate): 
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
            "binary": BYTEA,
            "boolean": BOOLEAN,
            "bool": BOOLEAN,
            "date": DATE,
            "datetime": DateTime,
            "timestamp": TIMESTAMP,
            "time": TIME,
            # "enum": ENUM,
            "float": FLOAT,
            "real": REAL,
            "json": MutableDict.as_mutable(JSON),
            "jsonb": MutableDict.as_mutable(JSONB),
            # "array": ARRAY, #FIXME column with array include array elemet type argument
            "numeric": NUMERIC,
            "money": MONEY,
            "macaddr": MACADDR,
            "inet": INET,
            "oid": OID,
            "uuid": UUIDType(binary=False),
        }.get(type_name.lower())


