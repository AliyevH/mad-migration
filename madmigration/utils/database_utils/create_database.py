import logging
from datetime import datetime
from sqlalchemy.sql import text

from madmigration.utils.helpers import generate_database_details
from .database_enum import DatabaseTypes
from errors import UnsupportedDatabase


def create_psql_db(database_name, **kwargs):
    def inner(connection):
        sql_text = text("CREATE DATABASE :database_name ENCODING :encoding TEMPLATE :template;")

        return connection.execute(sql_text, database_name=database_name, **kwargs)
    return inner

def create_mysql_db(database_name, **kwargs):
    def inner(connection):
        sql_text = text("CREATE DATABASE :database_name CHARACTER SET :charset COLLATE :collate;")

        return connection.execute(sql_text, database_name=database_name, **kwargs)
    return inner

def create_generic_db(database_name):
    def inner(connection):

        sql_text = text('CREATE DATABASE :database_name;')
        return connection.execute(sql_text, database_name=database_name)
    return inner

def create_mongo_db(database: str):
    """
    Not created until it gets content
    """
    def inner(mongo_client):
        db =  mongo_client[database]
        mycol = db["new_db"]
        mydict = {"created_at": datetime.now()}

        # returns an ID to ensure db creation
        return mycol.insert_one(mydict).inserted_id
    return inner

def create_database_strategy(url, engine):
    details = generate_database_details(url)
    creation_strategy = {
        DatabaseTypes.POSTGRES: create_psql_db(details.database, encoding='utf-8', template='template0'),
        DatabaseTypes.MYSQL: create_mysql_db(details.database, charset='utf8mb4', collate='utf8mb4_unicode_ci'),
        DatabaseTypes.SQLITE: create_generic_db(details.database),
        DatabaseTypes.ORACLE: create_generic_db(details.database),
        DatabaseTypes.MONGODB: create_mongo_db(details.database)
    }

    strategy = creation_strategy.get(details.dialect_name, None)
    if strategy is None:
        raise UnsupportedDatabase()

    try:
        return strategy(engine)
    except Exception as e:
        logging.error(e)


def async_create_psql_db(database_name, **kwargs):
    async def inner(connection):
        sql_text = text("CREATE DATABASE :database_name ENCODING :encoding TEMPLATE :template;")

        return await connection.execute(sql_text, database_name=database_name, **kwargs)
    return inner

def async_create_mysql_db(database_name, **kwargs):
    async def inner(connection):
        sql_text = text("CREATE DATABASE :database_name CHARACTER SET :charset COLLATE :collate;")

        return connection.execute(sql_text, database_name=database_name, **kwargs)
    return inner

def async_create_generic_db(database_name):
    async def inner(connection):

        sql_text = text('CREATE DATABASE :database_name;')
        return connection.execute(sql_text, database_name=database_name)
    return inner

def async_create_mongo_db(database: str):
    """
    Not created until it gets content
    """
    async def inner(mongo_client):
        db =  mongo_client[database]
        mycol = db["new_db"]
        mydict = {"created_at": datetime.now()}

        # returns an ID to ensure db creation
        return await mycol.insert_one(mydict).inserted_id
    return inner

async def create_database_strategy(url, connection):
    details = generate_database_details(url)
    creation_strategy = {
        DatabaseTypes.POSTGRES: async_create_psql_db(details.database, encoding='utf-8', template='template0'),
        DatabaseTypes.MYSQL: async_create_mysql_db(details.database, charset='utf8mb4', collate='utf8mb4_unicode_ci'),
        DatabaseTypes.SQLITE: async_create_generic_db(details.database),
        DatabaseTypes.ORACLE: async_create_generic_db(details.database),
        DatabaseTypes.MONGODB: async_create_mongo_db(details.database)
    }

    strategy = creation_strategy.get(details.dialect_name, None)
    if strategy is None:
        raise UnsupportedDatabase()

    try:
        return await strategy(connection)
    except Exception as e:
        logging.error(e)