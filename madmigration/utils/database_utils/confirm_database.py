import imp
import os
from copy import copy
from sqlite3 import NotSupportedError

import sqlalchemy as sa
from sqlalchemy.engine.url import make_url
from sqlalchemy.exc import OperationalError, ProgrammingError

from madmigration.utils.helpers import generate_database_details
from .database_enum import DatabaseTypes

def _get_scalar_result(engine, sql):
    with engine.connect() as conn:
        return conn.scalar(sql)

def run_database_exist_check(url: str, sql_text: str):
    try:
        engine = sa.create_engine(url)
        return bool(_get_scalar_result(engine, sql_text))
    except (ProgrammingError, OperationalError):
        return False
    finally:
        if engine:
            engine.dispose()

def confirm_psql_database(url: str, database: str):
    sql_text = "SELECT 1 FROM pg_database WHERE datname='%s'" % database
    return run_database_exist_check(url, sql_text)

def confirm_mysql_database(url: str,  database: str):
    sql_text = ("SELECT SCHEMA_NAME FROM INFORMATION_SCHEMA.SCHEMATA "
                    "WHERE SCHEMA_NAME = '%s'" % database)
    return run_database_exist_check(url, sql_text)

def generic_confirm_database(url):
    sql_text = 'SELECT 1'
    return run_database_exist_check(url, sql_text)

def confirm_sqlite_database(url):
    database = make_url(url).database
    if not os.path.isfile(database) or os.path.getsize(database) < 100:
        return False

    with open(database, 'rb') as f:
        header = f.read(100)
    return header[:16] == b'SQLite format 3\x00'


def decide_confirm_database_stratehy(url):
    details = generate_database_details(url)
    strategies = {
        DatabaseTypes.POSTGRES: confirm_psql_database,
        DatabaseTypes.MYSQL: confirm_mysql_database,
        DatabaseTypes.MSSQL: generic_confirm_database,
        # DatabaseTypes.MONGODB: '',
        DatabaseTypes.SQLITE: generic_confirm_database
    }

    strategy = strategies.get(details.dialect_name, None)
    if strategy is None:
        raise NotSupportedError
    return strategy(url)
    
