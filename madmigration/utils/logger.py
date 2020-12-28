import logging
import logging.config
import yaml
import os 
import coloredlogs

mad_path = os.path.abspath(os.curdir)
config_file = mad_path + "/madmigration/config/logger_config.yml"


def configure_logging():
    with open(config_file) as f:
        config = yaml.safe_load(f.read())
        logging.config.dictConfig(config)
        fmt = config.get("formatters").get("simple")
        coloredlogs.install(level="DEBUG", **fmt)