import os
import pytest
from madmigration.config.config_schema import ConfigSchema
from madmigration.config.conf import Config
import sys
import yaml


def config_schema_test():

    file = os.path.realpath('mysql.yaml')
    obj = Config(file)

    assert obj.version == obj.config_data.version
    assert obj.source_uri == obj.config_data.Configs[0].SourceConfig.get("dbURI")
    assert obj.destination_uri == obj.config_data.Configs[1].DestinationConfig.get("dbURI")
    assert obj.migrationTables == obj.config_data.migrationTables
    
    assert obj.config_file == file


