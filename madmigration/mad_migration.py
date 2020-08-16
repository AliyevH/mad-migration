from madmigration.db_init.connection_engine import SourceDB
from madmigration.db_init.connection_engine import DestinationDB
from madmigration.utils.helpers import detect_driver, get_cast_type, get_column_type
from sqlalchemy import Column, MetaData,Table
from pprint import pprint


class MadMigration:
    def __init__(self,migration_config):
        self.config = migration_config

        # Source and Destination DB Initialization with session
        self.sourceDB = SourceDB(self.config)
        self.destinationDB = DestinationDB(self.config)
        self.metadata = MetaData()

        # Source and Destination Database all tables (NOT MIGRATION!!!!)
        self.sourceDB_all_tables = self.sourceDB.engine.table_names()
        self.destinationDB_all_tables = self.destinationDB.engine.table_names()

        # All migration tables (Yaml file migrationTables)
        self.migration_tables = self.config.migrationTables

        # Destination DB Driver and name
        self.destinationDB_driver = self.destinationDB.engine.driver
        self.destinationDB_name = self.destinationDB.engine.name

    def test_func(self):
        # MysqlDB Migrate class
        for mt in self.migration_tables:
            migrate = detect_driver(self.destinationDB_driver)(mt.migrationTable)
            print(migrate.source_table)
            print(migrate.destination_table)
            for mc in migrate.columns:
                print(mc.dict())

    def create_tables(self):
        # create destination tables with options 

        for mig_tables in self.migration_tables:
            tablename = mig_tables.dict().get("migrationTable").get("DestinationTable").get("name")
            columns = []

            for column in mig_tables.dict().get("migrationTable").get("MigrationColumns"):
                column_type = get_column_type(column.get("destinationColumn")["options"].pop("type"))
                column.get("destinationColumn")["options"].pop("type_cast")
                col = Column(column.get("destinationColumn").get("name"),column_type,**column.get("destinationColumn").get("options"))
                columns.append(col)

            Table(
                tablename,self.metadata,
                *columns
            )

            self.metadata.create_all(self.destinationDB.engine)
