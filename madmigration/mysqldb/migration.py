from madmigration.config.config_schema import MigrationTablesSchema
from madmigration.config.config_schema import ColumnParametersSchema
from madmigration.config.config_schema import TablesInfo
from sqlalchemy import Column, Table, MetaData
from sqlalchemy.dialects.mysql import (
    VARCHAR,
    INTEGER,
    NVARCHAR,
    SMALLINT,
    SET,
    BIGINT,
    BINARY,
    BOOLEAN,
    CHAR,
    DATE,
    DATETIME,
    DECIMAL,
    ENUM,
    FLOAT,
    JSON,
    NUMERIC,
    TEXT,
)


class Migrate:
    def __init__(self, migration_table: TablesInfo):
        self.migration_tables = migration_table
        self.metadata = MetaData()
        self.parse_migration_tables()
        

    def parse_migration_tables(self):
        self.source_table = self.migration_tables.SourceTable
        self.destination_table = self.migration_tables.DestinationTable
        self.columns = self.migration_tables.MigrationColumns

    def parse_migration_columns(self, migration_columns: ColumnParametersSchema):
        self.source_column = migration_columns.sourceColumn
        self.destination_column = migration_columns.destinationColumn
        self.dest_options = migration_columns.destinationColumn.options.dict()
        # self.source_options = migration_columns.sourceColumn.options

    def create_tables(self, dest_engine):
        # create destination tables with options

        tablename = self.destination_table.get("name")
        temp_columns = []

        for column in self.columns:
            self.parse_migration_columns(column)
            self.dest_options.pop("foreign_keys")
            column_type = Migrate.get_column_type(
                self.dest_options.pop("type")
            )
            type_length = self.dest_options.pop("length")
            if type_length:
                column_type = column_type(type_length)
            self.dest_options.pop("type_cast")
            col = Column(
                self.destination_column.name,
                column_type,
                **self.dest_options
            )
            temp_columns.append(col)
        Table(tablename, self.metadata, *temp_columns)

        self.metadata.create_all(dest_engine)

    ###########################
    # Get class of db type #
    ###########################
    @staticmethod
    def get_column_type(type_name: str) -> object:
        """
        :param type_name: str
        :return: object class
        """
        return {
            "varchar": VARCHAR,
            "integer": INTEGER,
            "nvarchar": NVARCHAR,
            "smallint": SMALLINT,
            "set": SET,
            "bigint": BIGINT,
            "binary": BINARY,
            "boolean": BOOLEAN,
            "bool": BOOLEAN,
            "char": CHAR,
            "date": DATE,
            "datetime": DATETIME,
            "decimal": DECIMAL,
            "enum": ENUM,
            "float": FLOAT,
            "json": JSON,
            "numeric": NUMERIC,
            "text": TEXT,
        }.get(type_name.lower())
