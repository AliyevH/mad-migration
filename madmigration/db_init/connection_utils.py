from enum import Enum, auto
from madmigration.utils.database_utils.database_enum import DBHandler, DatabaseTypes
from .connection_engine import SQLDatabaseConnection, NoSQLDatabaseConnection


class ConfigLocation(Enum):
    SOURCE=auto()
    DESTINATION=auto()


def get_database_connection_object(database_name: DatabaseTypes):
    if database_name in [DatabaseTypes.MYSQL, DatabaseTypes.POSTGRES, DatabaseTypes.MSSQL, DatabaseTypes.SQLITE]:
        handler_name = DBHandler.SQL

    if database_name == DatabaseTypes.MONGODB:
        handler_name = DBHandler.MONGO

    return {
        DBHandler.SQL: SQLDatabaseConnection,
        DBHandler.MONGO: NoSQLDatabaseConnection
    }.get(handler_name)