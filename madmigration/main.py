from madmigration.db_init.connection_engine import SourceDB
from madmigration.db_init.connection_engine import DestinationDB
from madmigration.utils.helpers import detect_driver, get_cast_type, get_column_type
from sqlalchemy import Column, MetaData, Table
from madmigration.config.conf import Config
from madmigration.mysqldb.type_convert import get_type_object
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
from time import sleep


class Controller:
  

    def __init__(self, migration_config: Config):
        self.config = migration_config

        # Source and Destination DB Initialization with session
        self.sourceDB = SourceDB(self.config)
        self.destinationDB = DestinationDB(self.config)
        self.metadata = MetaData()

        # Source and Destination Database - all tables (NOT MIGRATION TABLES!!!)
        self.sourceDB_all_tables_names = self.sourceDB.engine.table_names()
        self.destinationDB_all_tables_names = self.destinationDB.engine.table_names()

        # All migration tables (Yaml file migrationTables)
        self.migration_tables = self.config.migrationTables

        # Destination DB Driver and name
        self.destinationDB_driver = self.destinationDB.engine.driver
        self.destinationDB_name = self.destinationDB.engine.name

        # Source DB Driver
        self.sourceDB_driver = self.sourceDB.engine.driver
    

    def __enter__(self):
        return self

    def __exit__(self, type, value, traceback):
        self.sourceDB.session.close()
        self.destinationDB.session.close()
        return True # we take care of error handling, wrap it up.

    

    def prepare_tables(self):
        # detect migration class
        migrate = detect_driver(self.destinationDB_driver)
        for migrate_table in self.migration_tables:
            mig = migrate(migrate_table.migrationTable,self.destinationDB.engine)
            mig.create_tables()
        migrate.create_fk_constraint(self.destinationDB.engine)

    def get_column_type_from_source_table(self, table_name, column_name):
        """
        Get type of column in source table from Source Database
        :param table_name: Table name
        :param column_name: Column name
        :return: Column type (Integer, Varchar, Float, Double, etc...)
        """
        tables = self.sourceDB.base.metadata.tables
        table = tables.get(table_name)
        for column in table.columns:
            if column.name == column_name:
                return column.type

    def run(self):

        # Looping in migrationTables
        for mt in self.migration_tables:
            self.destination_table = mt.migrationTable.DestinationTable
            count = 0

            # Migrate class is use based on driver
            Migrate = detect_driver(self.sourceDB_driver)

            # Instance of Migrate class
            migrate = Migrate(mt.migrationTable, self.sourceDB)
            migrate.parse_migration_tables()

            # Dictionary is used to keep data about destination column and type_cast format
            self.convert_info = {}

            # Columns List is used to keep source Columns names
            # We will send table name and source columns list to function "get_data_from_source_table"
            # get_data_from_source_table function will yield data with specified columns from row
            columns = []

            for column in migrate.columns:
                columns.append(column.sourceColumn.get("name"))

                if column.destinationColumn.options.type_cast:
                    self.convert_info[
                        column.destinationColumn.name] = column.destinationColumn.options.type_cast

            # self.source_data is data received (yield) from get_data_from_source_table function
            self.source_data = migrate.get_data_from_source_table(mt.migrationTable.SourceTable, columns)

            # Looping in self.source_data
            for data in self.source_data:
                for columns in mt.migrationTable.MigrationColumns:
                    source_column = columns.sourceColumn.get("name")
                    destination_column = columns.destinationColumn.name

                    if columns.destinationColumn.options.type_cast:
                        destination_type_cast = columns.destinationColumn.options.type_cast
                    else:
                        destination_type_cast = None

                    if self.convert_info.get(destination_column):
                        # ClassType is Class of data type (int, str, float, etc...)
                        # Using this ClassType we are converting data into format specified in type_cast
                        ClassType = get_type_object(destination_type_cast)

                        try:
                            if ClassType.__name__ == "uuid4":
                                data[destination_column] = ClassType()
                            else:
                                data[destination_column] = ClassType(data.pop(source_column))
                        except Exception as err:
                            print(err)
                            data[destination_column] = None
                    else:
                        data[destination_column] = data.pop(source_column)

                # print(data)

            print(getattr(self.destinationDB.base.classes, self.destination_table.get("name")))
            # print(self.destination_table.get("name"))












