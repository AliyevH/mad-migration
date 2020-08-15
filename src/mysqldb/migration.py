from config.conf import config
from config.config_schema import MigrationTablesSchema
from config.config_schema import ColumnParameters
from config.config_schema import TablesInfo


class Migrate:
    def __init__(self, migration_table: TablesInfo):
        self.migration_table = migration_table
        self.parse_migration_tables(self.migration_table)

    def parse_migration_tables(self, migration_table: MigrationTablesSchema):
        self.source_table = migration_table.SourceTable
        self.destination_table = migration_table.DestinationTable
        self.columns = migration_table.MigrationColumns

    def parse_migration_columns(self, migration_columns: ColumnParameters):
        self.source_column = migration_columns.sourceColumn
        self.destination_column = migration_columns.destinationColumn
        self.options = migration_columns.options

