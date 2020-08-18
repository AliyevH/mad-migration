import  os
import pytest
from madmigration.config.config_schema import ConfigSchema
from madmigration.config.conf import Config
import  sys
import  yaml


# # Config class generates configuration based on yaml file
# class Config:
#     def __init__(self, config_yaml):
#         self.config_file = config_yaml

#         with open(self.config_file) as f:
#             self.config_data = ConfigSchema(**yaml.load(f, Loader=yaml.FullLoader)) # noqa  E501
#         pprint(self.config_data.dict())
#         self.version = self.config_data.version
#         self.source_uri = self.config_data.Configs[0].SourceConfig.get("dbURI")
#         self.destination_uri = self.config_data.Configs[1].DestinationConfig.get("dbURI") # noqa  E501
#         self.migrationTables = self.config_data.migrationTables

def config_schema_test():

    file  = os.path.realpath('test.yaml')
    obj = Config(file)

    assert obj.version == obj.config_data.version
    assert obj.source_uri == obj.config_data.Configs[0].SourceConfig.get("dbURI")
    assert obj.destination_uri == obj.config_data.Configs[1].DestinationConfig.get("dbURI") # noqa  E501
    assert obj.migrationTables == obj.config_data.migrationTables
    
    assert obj.config_file == file


# config_schema_test()