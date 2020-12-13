from datetime import datetime
from sqlalchemy.schema import DropTable
from sqlalchemy.ext.compiler import compiles
import os
from pathlib import Path
from sqlalchemy import (
    Integer,
    String,
    DateTime,
    Date,
    BigInteger,
    VARCHAR,
    Float,
    TIMESTAMP
)
from madmigration.errors import FileDoesNotExists

from madmigration.mysqldb.migration import Migrate as mysql_migrate
from madmigration.postgresqldb.migration import Migrate as postgres_migrate

###########################
# Get class of cast #
###########################
def get_cast_type(type_name: str) -> object:
    """
    :param type_name: str
    :return: object class
    """
    return {
        'str': str,
        'string': str,
        'int': int,
        'integer': int,
        'float': float,
        'datetime': datetime,
        'varchar': VARCHAR
    }.get(type_name.lower())


###########################
# Get class of db type #
###########################
def get_column_type(type_name: str) -> object:
    """
    :param type_name: str
    :return: object class
    """
    return {
        'string': String,
        'integer': Integer,
        'biginteger': BigInteger,
        'float': Float,
        'datetime': DateTime,
        'date' : Date,
        'timestamp' : TIMESTAMP,
        'varchar': VARCHAR
    }.get(type_name.lower())


###########################
# Detect db driver fro migration #
###########################
def detect_driver(driver: str) -> object:
    """
    :param driver: str
    :return: object class
    """
    return {
        "mysqldb" : mysql_migrate,
        "pymysql": mysql_migrate,
        "mysql+pymysql" : mysql_migrate,
        "psycopg2": postgres_migrate  # heleki ozum verdim ki mende error vermesin

    }.get(driver)


@compiles(DropTable, "postgresql")
def _compile_drop_table(element, compiler, **kwargs):
    """ 
    Drop table cascade with foreignkeys
    https://stackoverflow.com/questions/38678336/sqlalchemy-how-to-implement-drop-table-cascade# 
    
    """
    return compiler.visit_drop_table(element) + " CASCADE"


def check_file(file):
    if Path(file).is_file() and os.access(file, os.R_OK):
        return True
        
    
def file_not_found(file):
    raise FileDoesNotExists(f"Given file does not exists file: {file}",)
