import asyncio
import functools
from datetime import datetime
from copy import copy

import gino
from sqlalchemy.schema import DropTable
from sqlalchemy.schema import ForeignKeyConstraint
from sqlalchemy.ext.compiler import compiles
from sqlalchemy.engine.url import make_url
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
    TIMESTAMP
)
from madmigration.errors import FileDoesNotExists
from madmigration.mysqldb.migration import MysqlMigrate
from madmigration.postgresqldb.migration import PgMigrate
from madmigration.mssql.migration import MssqlMigrate
from madmigration.mongodb.migration import MongoDbMigrate
import logging


logger = logging.getLogger(__name__)

__version__ = "0.1.7"

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
    if "///" in uri:
        database_name = uri.split("///")[-1]
    else:
        database_name = uri.split("/")[-1]

    return database_name


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
        ""
    ]
    return "\n".join(usage)


def goodby_message(message, exit_code=0):
    print(message, flush=True)
    logger.error(message)
    sys.exit(int(exit_code))


def run_await_funtion(loop=None):
    """
    a decorator to help run async functions like they were sync
    """
    if not loop:
        loop = asyncio.get_event_loop()

    if not loop.is_running():
        loop = asyncio.get_event_loop()

    def wrapper_function(func):
        @functools.wraps(func)
        def wrapped_function(*args, **kwargs):
            return loop.run_until_complete(func(*args, **kwargs))
        return wrapped_function

    return wrapper_function


@run_await_funtion()
async def aio_database_exists(url):
    async def get_scalar_result(engine, sql):
        conn = await engine.acquire()
        result = await conn.scalar(sql)
        await conn.release()
        await engine.close()
        return result

    def sqlite_file_exists(database):
        if not os.path.isfile(database) or os.path.getsize(database) < 100:
            return False

        with open(database, 'rb') as f:
            header = f.read(100)

        return header[:16] == b'SQLite format 3\x00'

    url = copy(make_url(url))
    database, url.database = url.database, None
    engine = await gino.create_engine(url)

    if engine.dialect.name == 'postgresql':
        text = "SELECT 1 FROM pg_database WHERE datname='%s'" % database
        result = await get_scalar_result(engine, text)
        return bool(result)

    elif engine.dialect.name == 'mysql':
        text = ("SELECT SCHEMA_NAME FROM INFORMATION_SCHEMA.SCHEMATA "
                "WHERE SCHEMA_NAME = '%s'" % database)
        result = await get_scalar_result(engine, text)
        return bool(result)

    elif engine.dialect.name == 'sqlite':
        if database:
            return database == ':memory:' or sqlite_file_exists(database)
        else:
            return True

    else:
        await engine.close()
        engine = None
        text = 'SELECT 1'
        try:
            url.database = database
            engine = await gino.create_engine(url)
            result = engine.scalar(text)
            await result.release()
            return True

        except (ProgrammingError, OperationalError):
            return False
        finally:
            if engine is not None:
                await engine.close()
