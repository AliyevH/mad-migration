import logging
from pymongo import MongoClient

from madmigration.utils.helpers import generate_database_details
from .database_enum import DatabaseTypes
from errors import UnsupportedDatabase
from utils.display import cmd_diplay_utiltity

# consider closures for more detailed approach
def create_psql_db(url, connection):
    text = "CREATE DATABASE {0} ENCODING '{1}' TEMPLATE {2}".format(
        quote(engine, database),
        encoding,
        quote(engine, template)
    )

    return connection.execute(text)

def create_mysql_db(url, connection):
    text = "CREATE DATABASE {0} CHARACTER SET = '{1}'".format(
        quote(connection, database),
        encoding
    )

    return connection.execute(text)

def create_generic_db(url, connection):
    text = 'CREATE DATABASE {0}'.format(quote(connection, database))

    return connection.execute(text)

def create_sqlite_db(url, connection):
    pass

# tweak
def create_mongo_db(url: str, mongo_client):
    return mongo_client[url.split("/")[-1]]

def create_database_strategy(url, engine):
    details = generate_database_details(url)
    creation_strategy = {
        DatabaseTypes.POSTGRES: create_psql_db,
        DatabaseTypes.MYSQL: create_mysql_db,
        DatabaseTypes.SQLITE: create_sqlite_db,
        DatabaseTypes.MONGODB: create_mongo_db
    }

    strategy = creation_strategy.get(details.dialect_name, None)
    if strategy is None:
        raise UnsupportedDatabase()

    try:
        return strategy(details.database, engine)
    except Exception as e:
        logging.error(e)