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
    def __init__(self, migration_table: TablesInfo, engine):
        self.sourceDB = engine
        self.migration_tables = migration_table
        self.metadata = MetaData()
        self.parse_migration_tables()

    def parse_migration_tables(self):
        """
        This function parses migrationTables from yaml file
        """
        self.source_table = self.migration_tables.SourceTable
        self.destination_table = self.migration_tables.DestinationTable
        self.columns = self.migration_tables.MigrationColumns

    def parse_migration_columns(self, migration_columns: ColumnParametersSchema):
        """
        This function parses migrationColumns from yaml file
        """
        self.source_column = migration_columns.sourceColumn
        self.destination_column = migration_columns.destinationColumn.dict()
        self.destination_options = migration_columns.destinationColumn.options.dict()
        # self.source_options = migration_columns.sourceColumn.options

    def get_table_attribute_from_base_class(self, source_table_name: str):
        """
        This function gets table name attribute from sourceDB.base.classes. Example sourceDB.base.class.(table name)
        Using this attribute we can query table using sourceDB.session
        :return table attribute
        """
        # for i in dir(self.sourceDB.base.classes):
        #     print(i)

        # print(" ---------- ")

        return getattr(self.sourceDB.base.classes, source_table_name)

    def get_data_from_source_table(self, source_table_name: str, source_columns: list):

        table = self.get_table_attribute_from_base_class(source_table_name.get("name"))

        rows = self.sourceDB.session.query(table).yield_per(1)

        for row in rows:
            data = {}
            for column in source_columns:
                data[column] = getattr(row, column)
            yield data







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

