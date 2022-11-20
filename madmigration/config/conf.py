import yaml
import json
import os
from madmigration.config.config_schema import ConfigSchema, NoSQLConfigSchema
from typing import IO, Any
from pprint import pprint


class Loader(yaml.SafeLoader):
    """YAML Loader with `!import` constructor."""

    def __init__(self, stream: IO) -> None:
        """Initialise Loader."""
        try:
            self._root = os.path.split(stream.name)[0]
        except AttributeError:
            self._root = os.path.curdir

        super().__init__(stream)


def construct_include(loader: Loader, node: yaml.Node) -> Any:
    """Include file referenced at node."""

    filename = os.path.abspath(
        os.path.join(loader._root, loader.construct_scalar(node))
    )
    extension = os.path.splitext(filename)[1].lstrip(".")

    with open(filename, "r") as f:
        if extension in ("yaml", "yml"):
            return yaml.load(f, Loader)
        elif extension in ("json",):
            return json.load(f)
        else:
            return "".join(f.readlines())


yaml.add_constructor("!import", construct_include, Loader)

# Config class generates configuration based on yaml file
class ConfigYamlManager:
    def __init__(self, config_yaml):
        self.destination_mongo = False
        self.config_file = config_yaml
        self.data = self.read_config_yml_file()

        self.config_section = self.get_config_section_from_yml()
        self.source_config_section = self.get_sourceDB_config_section_from_yml()
        self.destination_config_section = self.get_destinationDB_config_section_from_yml()
        self.destination_uri = self.get_destination_db_uri()
        self.source_uri = self.get_source_db_uri()
        self.config_schema = self.verify_and_choose_ConfigSchema_based_on_database_type(self.data)
        self.migrationTables = self.config_schema.migrationTables

    def get_config_section_from_yml(self):
        return self.data.get('Configs')
    
    def get_sourceDB_config_section_from_yml(self):
        return self.config_section[0].get('SourceConfig')

    def get_destinationDB_config_section_from_yml(self):
        return self.config_section[1].get('DestinationConfig')

    def read_config_yml_file(self):
        with open(self.config_file) as f:
            return yaml.load(f, Loader=Loader)

    def get_source_db_uri(self):
        return self.source_config_section.get('dbURI')

    def get_destination_db_uri(self):
        return self.destination_config_section.get('dbURI')

    def verify_and_choose_ConfigSchema_based_on_database_type(self, data):
        if "mongodb" in self.destination_uri:
            self.destination_mongo = True
            return NoSQLConfigSchema(**data, Loader=Loader)
        else:
            return ConfigSchema(**data, Loader=Loader)

    def collect_destination_tables(self):
        """Collects all tables that the program should create"""
        table_list = []
        for migrate_table in self.migrationTables:
            table_name = migrate_table.migrationTable.DestinationTable.name
            table_list.append(table_name)
        return table_list
