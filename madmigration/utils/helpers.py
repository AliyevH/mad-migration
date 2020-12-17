from datetime import datetime
from sqlalchemy.schema import DropTable
from sqlalchemy.schema import ForeignKeyConstraint
from sqlalchemy.ext.compiler import compiles
from typing import Union
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

from madmigration.mysqldb.migration import MysqlMigrate
from madmigration.postgresqldb.migration import PgMigrate

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
# Detect db driver fro migration #
###########################
def detect_driver(driver: str) -> Union[MysqlMigrate, PgMigrate]:
    """
    :param driver: str
    :return: object class
    """
    return {
        "mysqldb" : MysqlMigrate,
        "mysql+mysqldb": MysqlMigrate,
        "pymysql": MysqlMigrate,
        "mysql+pymysql" : MysqlMigrate,
        "mariadb+pymsql" : MysqlMigrate,
        "psycopg2": PgMigrate,  
        "postgresql+psycopg2": PgMigrate,
        "postgresql+pg8000": PgMigrate,
       # "postgresql+asyncpg": postgres_migrate,
       # "asyncpg": postgres_migrate
    }.get(driver)


@compiles(DropTable, "postgresql")
def _compile_drop_table(element, compiler, **kwargs):
    """
    Drop table cascade with foreignkeys
    https://stackoverflow.com/questions/38678336/sqlalchemy-how-to-implement-drop-table-cascade# 
    """
    return compiler.visit_drop_table(element) + " CASCADE"



@compiles(ForeignKeyConstraint, "mysql", "mariadb")
def process(element, compiler, **kw):
    element.deferrable = element.initially = None
    return compiler.visit_foreign_key_constraint(element, **kw)


def check_file(file):
    return Path(file).is_file() and os.access(file, os.R_OK)

def file_not_found(file):
    raise FileDoesNotExists(f"Given file does not exists file: {file}",)


def issue_url():
    return "https://github.com/MadeByMads/mad-migration/issues"

def app_name():
    return "madmigrate"


def parse_uri(uri):
    if "///" in uri:
        database_name  = uri.split("///")[-1]
    else:
        database_name = uri.split("/")[-1]

    return database_name