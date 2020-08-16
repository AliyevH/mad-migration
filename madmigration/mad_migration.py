from db_init.connection_engine import SourceDB
from db_init.connection_engine import DestinationDB
from utils.helpers import detect_driver



class MadMigration:
    def __init__(self,migration_config):
        self.config = migration_config

        # Source and Destination DB Initialization with session
        self.sourceDB = SourceDB(self.config)
        self.destinationDB = DestinationDB(self.config)


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
