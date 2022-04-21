import logging
from sqlalchemy import create_engine, MetaData, event, Table
from sqlalchemy.orm import Session
from sqlalchemy.ext.automap import automap_base
from pymongo import MongoClient
from pymongo.uri_parser import parse_uri as mongo_parse_uri
from sqlalchemy.engine.url import make_url as sql_parse_uri

from madmigration.utils.helpers import parse_uri
from madmigration.utils.helpers import database_not_exists, goodby_message
from madmigration.utils.database_utils import create_database_strategy, confirm_database_strategy

from madmigration.errors import CouldNotConnectError, MissingSourceDBError
from .connection_utils import ConfigLocation
from .base_engine import DatabaseBaseConnection


logger = logging.getLogger(__name__)


@event.listens_for(Table, "after_parent_attach")
def before_parent_attach(target, parent):
    if not target.primary_key and "id" in target.c:
        print(target)



class SQLDatabaseConnection(DatabaseBaseConnection):
    def __init__(self, connection_uri: str, config_location: ConfigLocation): 
        self.connection_uri = connection_uri
        self.engine = self._create_connection()
        self.config_location = config_location

        existing_db = self._check_database_exist()

        if config_location is ConfigLocation.SOURCE and existing_db is False:
            raise MissingSourceDBError()

        if config_location is ConfigLocation.DESTINATION and existing_db is False:
            self._create_database

        base = automap_base()
        base.prepare(self.engine, reflect=True)
        self.session = Session(self.engine, autocommit=False, autoflush=False)

    @property
    def driver(self):
        return sql_parse_uri(self.connection_uri).get_dialect().driver

    @property
    def db_name(self):
        return sql_parse_uri(self.connection_uri).database

    def all_db_tables(self):
        return self.engine.table_names()

    def _check_database_exist(self):
        return confirm_database_strategy(self.connection_uri)

    def _create_database(self):
        while True:
            msg = input(f"Destination database does not exists, would you like to create it in the destination?(y/n) ")
            if msg.lower() == "y":
                with self.engine.connect() as conn:
                    return create_database_strategy(self.connection_uri, conn)
            elif msg.lower() == "n":
                return goodby_message("Destination database does not exist \nExiting ...", 0)

    def _create_connection(self):
        try:
            if not self.engine:
                engine = create_engine(self.connection_uri, echo=False)
            return engine
        except Exception as e:
            logging.error(e)
            raise CouldNotConnectError(e)

    def close(self):
        self.session.close()
        return self.engine.dispose()



class NoSQLDatabaseConnection(DatabaseBaseConnection):
    def __init__(self, connection_uri: str, config_location: ConfigLocation): 
        self.connection_uri = connection_uri
        self.config_location = config_location
        existing_db = self._check_database_exist()

        if config_location is ConfigLocation.SOURCE and existing_db is False:
            raise MissingSourceDBError()

        if config_location is ConfigLocation.DESTINATION and existing_db is False:
            self._create_database

        # The engine is created after checking the database exists, such that if it does this isnt
        # ran before it fails
        self.engine = self._create_connection()

    @property
    def driver(self):
        return 'mongodb'

    @property
    def db_name(self):
        return mongo_parse_uri(self.connection_uri)['database']

    def _check_database_exist(self):
        return confirm_database_strategy(self.connection_uri)

    def _create_database(self):
        while True:
            msg = input(f"Destination database does not exists, would you like to create it in the destination?(y/n) ")
            if msg.lower() == "y":
                return create_database_strategy(self.connection_uri, self.engine)
            elif msg.lower() == "n":
                return goodby_message("Destination database does not exist \nExiting ...", 0)

    def _create_connection(self):
        database = mongo_parse_uri(self.connection_uri).get('database', None)
        try:
            if not self.engine:
                engine = MongoClient(self.connection_uri)[database]
            return engine
        except Exception as e:
            logging.error(e)
            raise CouldNotConnectError()

    def all_db_tables(self):
        """
        Collections in MongoDb are the equivalent of tables in SQl. This returns all
        the collections in the database
        """
        self.engine.list_collection_names(include_system_collections=False)

    def close(self):
        return None
