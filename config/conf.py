import yaml
from config.config_schema import ConfigSchema


class Config:
    def __init__(self, config_yaml):
        self.config_file = config_yaml

        with open(self.config_file) as f:
            self.config_data = ConfigSchema(**yaml.load(f, Loader=yaml.FullLoader))

        self.version = self.config_data.version
        self.source_uri = self.config_data.Configs[0].SourceConfig.get("dbURI")
        self.destination_uri = self.config_data.Configs[1].DestinationConfig.get("dbURI")
        self.migrationTables = self.config_data.migrationTables



# Create Table in Destination Database
# class InitTables:
#     def __init__(self, config: ConfigSchema):
#         self.config = config
#         self.uri = self.config.Configs[1].DestinationConfig.get("dbURI")
#         self.migration_tables = self.config.migrationTables
#
#         self.parse_columns()
#
#     def get_type(self, x):
#         return {
#             'str': str,
#             'string': str,
#
#             'int': int,
#             'integer': int,
#
#             'float': float,
#             'datetime': datetime
#         }.get(x)
#
#     def parse_tables(self):
#         for mt in self.migrationTables:
#             for k, v in mt.items():
#                 self.create = v.get("Create")
#                 self.source_table_name = v.get("SourceTableName")
#                 self.destination_table_name = v.get("DestinationTableName")
#                 self.migration_columns = v.get("MigrationColumns")
#
#     def parse_columns(self):
#         for mc in self.migration_columns:
#             for k, v in mc.items():
#                 print(k, v)
#
#     def parse_column_options(self):
#         self.type_cast = self.get_type(self.column_options.get("type_cast"))
#         self.unique = self.column_options.get("unique", False)
#         self.fk_key = self.column_options.get("fk_key", False)
#         self.nullable = self.column_options.get("nullable", False)
#         self.index = self.column_options.get("index", False)
#         self.on_delete = self.column_options.get("on_delete", "CASCADE")

