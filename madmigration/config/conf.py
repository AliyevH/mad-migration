import yaml
from madmigration.config.config_schema import ConfigSchema,NoSQLConfigSchema
from pprint import pprint


# Config class generates configuration based on yaml file
class Config:
    def __init__(self, config_yaml):
        self.config_file = config_yaml

        with open(self.config_file) as f:
            data = yaml.load(f, Loader=yaml.FullLoader)
       
            self.select_config(data)
        
      
        self.version = self.config_data.version
        self.source_uri = self.config_data.Configs[0].SourceConfig.get("dbURI")
        self.destination_uri = self.config_data.Configs[1].DestinationConfig.get("dbURI") # noqa  E501
        self.migrationTables = self.config_data.migrationTables

    def select_config(self, data):

        destination_DB = data.get("Configs")[1]

        if "mongodb" in destination_DB.get("DestinationConfig").get("dbURI"):

            self.config_data = NoSQLConfigSchema(**data, Loader=yaml.FullLoader) # noqa  E501
            self.destination_mongo =True
            
        else:
            self.config_data = ConfigSchema(**data, Loader=yaml.FullLoader) # noqa  E501
            self.destination_mongo = False