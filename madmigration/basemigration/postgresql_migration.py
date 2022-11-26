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
from madmigration.basemigration.base_migration import BaseMigrate
from madmigration.config.conf import ConfigYamlManager


class PgMigrate(BaseMigrate): 
    def __init__(self, config: ConfigYamlManager, source_db_operations, destination_db_operations):
        super().__init__(config, source_db_operations, destination_db_operations)

    @staticmethod
    def get_column_type(type_name: str) -> object:
        """Get class of db type"""
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


