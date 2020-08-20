from datetime import datetime
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

from madmigration.mysqldb.migration import Migrate as mysql_migrate


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
        "psycopg2": mysql_migrate  # heleki ozum verdim ki mende error vermesin

    }.get(driver)
