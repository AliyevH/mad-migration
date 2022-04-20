import asyncio
import functools
import logging
import gino
from datetime import datetime
from copy import copy

from sqlalchemy.schema import DropTable
from sqlalchemy.schema import ForeignKeyConstraint
from sqlalchemy.ext.compiler import compiles
from sqlalchemy.engine.url import make_url as sql_parse_uri
from sqlalchemy.exc import ProgrammingError
from sqlalchemy.exc import OperationalError
from typing import Union
import os
import sys
from pathlib import Path
from sqlalchemy import (
    Integer,
    String,
    DateTime,
    Date,
    BigInteger,
    VARCHAR,
    Float,
    TIMESTAMP,
)
from pymongo.uri_parser import parse_uri as mongo_parse_uri

from madmigration.mysqldb.migration import MysqlMigrate
from madmigration.postgresqldb.migration import PgMigrate
from madmigration.mssql.migration import MssqlMigrate
from madmigration.mongodb.migration import MongoDbMigrate

from utils_response import DatabaseDetails


logger = logging.getLogger(__name__)

__version__ = "0.1.8beta"

###########################
# Get class of cast #
###########################


def get_cast_type(type_name: str) -> object:
    """
    :param type_name: str
    :return: object class
    """
    return {
        "str": str,
        "string": str,
        "int": int,
        "integer": int,
        "float": float,
        "datetime": datetime,
        "varchar": VARCHAR,
    }.get(type_name.lower())


###########################
# Detect db driver fro migration #
###########################
def detect_driver(driver: str) -> Union[MysqlMigrate, PgMigrate, MongoDbMigrate]:
    """
    :param driver: str
    :return: object class
    """
    return {
        "mysqldb": MysqlMigrate,
        "mysql+mysqldb": MysqlMigrate,
        "pymysql": MysqlMigrate,
        "mysql+pymysql": MysqlMigrate,
        "mariadb+pymsql": MysqlMigrate,
        "psycopg2": PgMigrate,
        "pg8000": PgMigrate,
        "pyodbc": MssqlMigrate,
        "mongodb": MongoDbMigrate
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
    logger.error(f"Given file does not exists file: {file}")
    sys.exit(1)
    # raise FileDoesNotExists(f"Given file does not exists file: {file}")


def issue_url():
    return "https://github.com/MadeByMads/mad-migration/issues"


def app_name():
    return "madmigrate"


def parse_uri(uri):
    return sql_parse_uri(uri).database


def database_not_exists(database):
    """This function will be executed if there is no database exists """

    database = parse_uri(database)

    usage = [
        "",
        f"😭 Error: Source database '{database}'  does not exists",
        "",
        f"Run '{app_name()} --help' for usage.",
        "",
        f"🥳  if you think something is wrong please feel free to open issues 👉'{issue_url()}'👈 ",
        "",
        "Exiting ...",
        "",
    ]
    return "\n".join(usage)


def goodby_message(message, exit_code=0):
    print(message, flush=True)
    logger.error(message)
    sys.exit(int(exit_code))


def generate_database_details(url):
    # use regular expressions to find format for different database configurations for extendibility
    if "mongodb" in url:
        item = mongo_parse_uri(url)
        database = item.database,
        dialect_name = 'mongodb'
        dialect_driver = 'mongodb'
    else:
        item = sql_parse_uri(url)
        database = item.database,
        dialect_name = item.get_dialect().name
        dialect_driver = item.get_dialect().driver

    return DatabaseDetails(
        database,
        dialect_name,
        dialect_driver
    )
