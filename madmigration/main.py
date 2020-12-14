from madmigration.db_init.connection_engine import SourceDB
from madmigration.db_init.connection_engine import DestinationDB
from madmigration.utils.helpers import detect_driver, get_cast_type, get_column_type
from sqlalchemy import Column, MetaData, Table
from madmigration.config.conf import Config
from madmigration.mysqldb.type_convert import get_type_object
from sqlalchemy import insert
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
        self.source_db = SourceDB(self.config)
        self.destination_db = DestinationDB(self.config)
        self.metadata = MetaData()

        # Source and Destination Database - all tables (NOT MIGRATION TABLES!!!)
        self.sourcedb_all_tables_names = self.source_db.engine.table_names()
        self.destinationdb_all_tables_names = self.destination_db.engine.table_names()

        # All migration tables (Yaml file migrationTables)
        self.migration_tables = self.config.migrationTables

        # Destination DB Driver and name
        self.destinationdb_driver = self.destination_db.engine.driver
        self.destinationdb_name = self.destination_db.engine.name

        # Source DB Driver
        self.sourcedb_driver = self.source_db.engine.driver
    

    def __enter__(self):
        return self

    def __exit__(self, type, value, traceback):
        self.source_db.session.close()
        self.destination_db.session.close()
        return True # we take care of error handling, wrap it up.

    

    def run_table_migrations(self):
        # detect migration class
        migrate = detect_driver(self.destinationdb_driver)
        
        mig = migrate(self.config,self.destination_db)
        mig.prepare_tables()
        # print(mig.tables_must_create)
        # print(mig.table_list)
        mig.create_tables()
        mig.create_fk_constraint()
            
        
        # migrate.create_fk_constraint(self.destination_db.engine)

    def get_column_type_from_source_table(self, table_name, column_name):
        """
        Get type of column in source table from Source Database
        :param table_name: Table name
        :param column_name: Column name
        :return: Column type (Integer, Varchar, Float, Double, etc...)
        """
        tables = self.source_db.base.metadata.tables
        table = tables.get(table_name)
        for column in table.columns:
            if column.name == column_name:
                return column.type

    def run(self):
        
        # Looping in migrationTables
        for mt in self.migration_tables:
            self.destination_table = mt.migrationTable.DestinationTable

            # Migrate class is use based on driver
            Migrate = detect_driver(self.sourcedb_driver)
            
            # Instance of Migrate class
            migrate = Migrate(mt.migrationTable, self.source_db)
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

            for source_data in self.source_data:
                new_data = Migrate.type_cast(data_from_source=source_data, mt=mt, convert_info=self.convert_info)
                Migrate.insert_data(engine=self.destination_db, table_name=self.destination_table.name, data=new_data)
            
            # count = 0
            # from time import sleep
            # for data in Migrate.loop_in_data(self.source_data, mt, self.convert_info):
            #     count += 1
            #     print("count: ",count, "id: ", data.get("id"))
            #     print(self.destination_table.name)
            #     sleep(1)
                # Migrate.insert_data(engine=self.destination_db, table_name=self.destination_table.name, data=data)
        



                













