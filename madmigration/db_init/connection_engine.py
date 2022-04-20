from abc import ABC, abstractmethod
import logging

from sqlalchemy import create_engine, MetaData, event, Table
from sqlalchemy.orm import Session
from sqlalchemy.ext.automap import automap_base
from pymongo import MongoClient

from madmigration.utils.helpers import parse_uri
from madmigration.utils.helpers import database_not_exists, goodby_message
from madmigration.utils.database_utils import create_database_strategy, confirm_database_strategy

from madmigration.errors import CouldNotConnectError, MissingSourceDBError
from .connection_utils import ConfigLocation


logger = logging.getLogger(__name__)


@event.listens_for(Table, "after_parent_attach")
def before_parent_attach(target, parent):
    if not target.primary_key and "id" in target.c:
        print(target)


class DatabaseConnection(ABC):
    @abstractmethod
    def _check_database_exist(self):
        raise NotImplementedError()

    @abstractmethod
    def _create_database(self):
        raise NotImplementedError()

    @abstractmethod
    def _create_connection(self):
        raise NotImplemented


class SQLDatabaseConnection(DatabaseConnection):
    def __init__(self, connection_uri: str, config_location: ConfigLocation): 
        self.connection_uri = connection_uri
        self.engine = self._create_connection()
        self.config_location = config_location

        existing_db = self._check_database_exist()

        if config_location is ConfigLocation.SOURCE and existing_db is False:
            raise MissingSourceDBError()

        if config_location is ConfigLocation.DESTINATION and existing_db is False:
            self._create_database

    def _check_database_exist(self):
        return confirm_database_strategy(self.connection_uri)

    def _create_database(self):
        with self.engine.connect() as conn:
            return create_database_strategy(self.connection_uri, conn)

    def _create_connection(self):
        try:
            if not self.engine:
                engine = create_engine(self.connection_uri, echo=False)
            return engine
        except Exception as e:
            logging.error(e)
            raise CouldNotConnectError(e)


class NoSQLDatabaseConnection(DatabaseConnection):
    def __init__(self, connection_uri: str, config_location: ConfigLocation): 
        self.connection_uri = connection_uri
        self.engine = self._create_connection()
        self.config_location = config_location

        existing_db = self._check_database_exist()

        if config_location is ConfigLocation.SOURCE and existing_db is False:
            raise MissingSourceDBError()

        if config_location is ConfigLocation.DESTINATION and existing_db is False:
            self._create_database

    def _check_database_exist(self):
        return confirm_database_strategy(self.connection_uri)

    def _create_database(self):
        return create_database_strategy(self.connection_uri, self.engine)

    def _create_connection(self):
        try:
            if not self.engine:
                engine = MongoClient(self.connection_uri)
            return engine
        except Exception as e:
            logging.error(e)
            raise CouldNotConnectError()


class SourceDB:
    def __init__(self, source_uri):
        if not database_exists(source_uri):
            goodby_message(database_not_exists(source_uri), 0)
        self.base = automap_base()
        self.engine = create_engine(source_uri, echo=False)
        self.base.prepare(self.engine, reflect=True)
        self.session = Session(self.engine, autocommit=False, autoflush=False)


class DestinationDB:
    def __init__(self, destination_uri):
        self.check_for_or_create_database(destination_uri)

        self.base = automap_base()
        self.engine = create_engine(destination_uri)
        # self.base.prepare(self.engine, reflect=True)
        self.session = Session(self.engine, autocommit=False, autoflush=False)

    def check_for_or_create_database(self, destination_uri, check_for_database: callable = database_exists):
        if not check_for_database(destination_uri):
            while True:
                database = parse_uri(destination_uri)
                msg = input(f"The database {database} does not exists, would you like to create it in the destination?(y/n) ")
                if msg.lower() == "y":
                    try:
                        create_database(destination_uri)
                        logger.info("Database created..")
                        break
                    except Exception as err:
                        goodby_message(database_not_exists(destination_uri), 1)
                    break
                elif msg.lower() == "n":
                    goodby_message("Destination database does not exist \nExiting ...", 0)
                    break
                print("Please, select command")
