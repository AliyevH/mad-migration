import yaml
from datetime import datetime

class Config:
    def __init__(self, config_yaml):
        self.config_file = config_yaml

        with open(self.config_file) as f:
            self.config_data = yaml.load(f, Loader=yaml.FullLoader)

        self.version = self.config_data.get("version")
        self.config = self.config_data.get("Config")

        self.sourceConfig = self.config[0].get("SourceConfig")
        self.destinationConfig = self.config[1].get("DestinationConfig")

        self.sourceURI = self.sourceConfig.get("dbURI")
        self.destinationURI = self.destinationConfig.get("dbURI")

        self.migrationTables = self.config_data.get("migrationTables")

        self.prepare_connection_string()

        self.parse_tables()
        self.parse_columns()

    def parse_tables(self):
        for mt in self.migrationTables:
            for k, v in mt.items():
                self.create = v.get("Create")
                self.source_table_name = v.get("SourceTableName")
                self.destination_table_name = v.get("DestinationTableName")
                self.migration_columns = v.get("MigrationColumns")

    def parse_columns(self):
        for mc in self.migration_columns:
            for k, v in mc.items():
                print(k, v)


# Create Table in Destination Database
class InitDestinationTables:
    def __init__(self, uri, table_name, column_name, **options):
        self.uri = uri
        self.table_name = table_name
        self.column_name = column_name
        self.column_options = options

        self.parse_columns()

    def get_type(self, x):
        return {
            'str': str,
            'string': str,

            'int': int,
            'integer': int,

            'float': float,
            'datetime': datetime
        }.get(x)

    def parse_column_options(self):
        self.type_cast = self.get_type(self.column_options.get("type_cast"))
        self.unique = self.column_options.get("unique", False)
        self.fk_key = self.column_options.get("fk_key", False)
        self.nullable = self.column_options.get("nullable", False)
        self.index = self.column_options.get("index", False)
        self.on_delete = self.column_options.get("on_delete", "CASCADE")

        
