import pytest
from madmigration.config.conf import Config
from madmigration.utils.helpers import  get_cast_type, get_column_type, detect_driver
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
from datetime import  datetime
from madmigration.mysqldb.migration import Migrate as mysql_migrate
from madmigration.postgresqldb.migration import Migrate as postgres_migrate


def get_cast_type_test(temp_data):

    assert get_cast_type(temp_data[0].lower()) == str
    assert get_cast_type(temp_data[1]) == str
    assert get_cast_type(temp_data[2]) == int
    assert get_cast_type(temp_data[3]) == int
    assert get_cast_type(temp_data[5]) == float
    assert get_cast_type(temp_data[6]) == datetime


def get_column_type_test(temp_data):

    assert get_column_type(temp_data[1]) == String
    assert get_column_type(temp_data[3].lower()) == Integer
    assert get_column_type(temp_data[4]) == BigInteger
    assert get_column_type(temp_data[5]) == Float
    assert get_column_type(temp_data[6]) == DateTime
    assert get_column_type(temp_data[8]) == TIMESTAMP
    assert get_column_type(temp_data[9]) == VARCHAR


def detect_driver_test():
      
    assert detect_driver("mysqldb") == mysql_migrate
    assert detect_driver("psycopg2") == postgres_migrate



