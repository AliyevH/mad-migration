import logging

from sqlalchemy import event, Table
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.engine.url import make_url as sql_parse_uri

from motor.motor_asyncio import AsyncIOMotorClient
from pymongo.uri_parser import parse_uri as mongo_parse_uri

from madmigration.utils.helpers import goodby_message
from madmigration.utils.database_utils import async_create_database_strategy, async_confirm_database_strategy
from madmigration.errors import CouldNotConnectError, MissingSourceDBError
from .connection_utils import ConfigLocation
from .base_engine import DatabaseBaseConnection
from madmigration.utils.helpers import (
    goodby_message,
)


@event.listens_for(Table, "after_parent_attach")
def before_parent_attach(target, parent):
    if not target.primary_key and "id" in target.c:
        print(target)


class AsyncSQLDatabaseConnection(DatabaseBaseConnection):
    """
    This class is instatiated with the async_create_connection to create an 
    async connection engine class for use throughout madmigration. Do not
    initiate this class with __init__
    """
    @classmethod
    async def async_create_connection(cls, connection_uri: str, config_location: ConfigLocation):
        cls.connection_uri = connection_uri
        cls.engine = await cls._create_connection()
        cls.config_location = config_location

        existing_db = await cls._check_database_exist()

        if config_location is ConfigLocation.SOURCE and existing_db is False:
            raise MissingSourceDBError()

        if config_location is ConfigLocation.DESTINATION and existing_db is False:
            await cls._create_database

        base = automap_base()
        base.prepare(cls.engine, reflect=True)
        cls.session = AsyncSession(cls.engine, autocommit=False, autoflush=False)

    @property
    def driver(self):
        return sql_parse_uri(self.connection_uri).get_dialect().driver

    @property
    def db_name(self):
        return sql_parse_uri(self.connection_uri).database

    async def all_db_tables(self):
        return await self.engine.table_names()

    async def _check_database_exist(self):
        return await async_confirm_database_strategy(self.connection_uri)

    async def _create_database(self):
        while True:
            msg = input(f"Destination database does not exists, would you like to create it in the destination?(y/n) ")
            if msg.lower() == "y":
                async with self.engine.begin() as conn:
                    return await async_create_database_strategy(self.connection_uri, conn)
            elif msg.lower() == "n":
                return goodby_message("Destination database does not exist \nExiting ...", 0)

    async def _create_connection(self):
        try:
            if not self.engine:
                engine = create_async_engine(self.connection_uri, echo=False)
            return engine
        except Exception as e:
            logging.error(e)
            raise CouldNotConnectError(e)

    async def close(self):
        await self.session.close()
        return await self.engine.dispose()


class AsyncNoSQLDatabaseConnection(DatabaseBaseConnection):
    """
    This class is instatiated with the async_create_connection to create an 
    async connection engine class for use throughout madmigration. Do not
    initiate this class with __init__
    """
    @classmethod
    async def async_create_connection(cls, connection_uri: str, config_location: ConfigLocation):
        cls.connection_uri = connection_uri
        cls.config_location = config_location
        existing_db = await cls._check_database_exist()

        if config_location is ConfigLocation.SOURCE and existing_db is False:
            raise MissingSourceDBError()

        if config_location is ConfigLocation.DESTINATION and existing_db is False:
            await cls._create_database

        # The engine is created after checking the database exists, such that if it does this isnt
        # ran before it fails
        cls.engine = await cls._create_connection()

    @property
    def driver(self):
        return 'mongodb'

    @property
    def db_name(self):
        return mongo_parse_uri(self.connection_uri)['database']

    async def _check_database_exist(self):
        return await async_confirm_database_strategy(self.connection_uri)

    async def _create_database(self):
        while True:
            msg = input(f"Destination database does not exists, would you like to create it in the destination?(y/n) ")
            if msg.lower() == "y":
                return await async_create_database_strategy(self.connection_uri, self.engine)
            elif msg.lower() == "n":
                return goodby_message("Destination database does not exist \nExiting ...", 0)

    async def _create_connection(self):
        database = mongo_parse_uri(self.connection_uri).get('database', None)
        try:
            if not self.engine:
                engine = AsyncIOMotorClient(self.connection_uri, serverSelectionTimeoutMS=5000)[database]
            return engine
        except Exception as e:
            logging.error(e)
            raise CouldNotConnectError()

    async def all_db_tables(self):
        """
        Collections in MongoDb are the equivalent of tables in SQl. This returns all
        the collections in the database
        """
        return await self.engine.list_collection_names(include_system_collections=False)

    async def close(self):
        return None
