import yaml
import json
import os
from typing import IO, Any
from pprint import pprint
from madmigration.config.config_schema import SQLConfigSchema, NoSQLConfigSchema
from madmigration.errors import ConfFileDoesNotExists
from madmigration.utils.helpers import check_file
from utils.display import cmd_diplay_utiltity



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


"""
What does it configure, 
Does it configure the migration class, does it configure the operations class?

I think it should be the operations class
"""

# Config class generates configuration based on yaml file
class Config:
    def __init__(self, config_yaml):
        self.config_file = config_yaml

        with open(self.config_file) as f:
            data = yaml.load(f, Loader=Loader)
            self.select_config(data)

        self.version = self.config_data.version
        self.source_uri = self.config_data.SourceConfig.get("dbURI")
        self.destination_uri = self.config_data.DestinationConfig.get(
            "dbURI"
        )  # noqa  E501
        self.migrationTables = self.config_data.migrationTables
        # self.database_type

    def select_config(self, data):

        destination_DB = data.get("Configs").get('DestinationConfig')

        if "mongodb" in destination_DB.get("dbURI"):

            self.config_data = NoSQLConfigSchema(**data, Loader=Loader)  # noqa  E501
            self.destination_mongo = True

        else:
            self.config_data = SQLConfigSchema(**data, Loader=Loader)  # noqa  E501
            self.destination_mongo = False


    def validate_conf_file_exist(self, file_path):
        if not check_file(file_path) and not os.path.splitext(file_path)[-1] not in ['.json', '.yaml', '.yml']:
            cmd_diplay_utiltity.display_configuration_file_missing()
            raise ConfFileDoesNotExists()

        return file_path