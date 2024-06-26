import logging

from sqlalchemy.dialects.mysql import (
    BIGINT,
    BINARY,
    BOOLEAN,
    CHAR,
    DATE,
    DATETIME,
    DECIMAL,
    ENUM,
    FLOAT,
    INTEGER,
    JSON,
    NUMERIC,
    NVARCHAR,
    SET,
    SMALLINT,
    TEXT,
    VARCHAR,
)

from madmigration.basemigration.base_migration import BaseMigrate
from madmigration.config.conf import ConfigYamlManager

logger = logging.getLogger(__name__)


class MysqlMigrate(BaseMigrate):
    def __init__(self, config: ConfigYamlManager):
        super().__init__(config)

    @staticmethod
    def get_column_type(type_name: str) -> object:
        """Get class of db type
        :param type_name: str
        :return: object class
        """
        return {
            "string": VARCHAR,
            "varchar": VARCHAR,
            "integer": INTEGER,
            "nvarchar": NVARCHAR,
            "smallint": SMALLINT,
            "set": SET,
            "bigint": BIGINT,
            "binary": BINARY,
            "boolean": BOOLEAN,
            "bool": BOOLEAN,
            "char": CHAR,
            "date": DATE,
            "datetime": DATETIME,
            "decimal": DECIMAL,
            "enum": ENUM,
            "float": FLOAT,
            "json": JSON,
            "numeric": NUMERIC,
            "text": TEXT,
            "uuid": CHAR(36),
        }.get(type_name.lower())
