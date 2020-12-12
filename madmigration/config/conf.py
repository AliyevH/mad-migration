import yaml
from madmigration.config.config_schema import ConfigSchema
from pprint import pprint


# Config class generates configuration based on yaml file
class Config:
    def __init__(self, config_yaml):
        self.config_file = config_yaml

        with open(self.config_file) as f:
            self.config_data = ConfigSchema(**yaml.load(f, Loader=yaml.FullLoader)) # noqa  E501
        # pprint(self.config_data.dict())
        self.version = self.config_data.version
        self.source_uri = self.config_data.Configs[0].SourceConfig.get("dbURI")
        self.destination_uri = self.config_data.Configs[1].DestinationConfig.get("dbURI") # noqa  E501
        self.migrationTables = self.config_data.migrationTables


# config = Config("postgres.yaml")
config = Config("test.yaml")