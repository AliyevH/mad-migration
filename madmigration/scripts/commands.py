import click
import math
import random
import time
import sys
from madmigration.config.conf import  Config
# from madmigration.config.conf import config

from madmigration.main import Controller


@click.group()
def cli():
    """Controller group Cli"""
    

@cli.command(help='simple Migrate ready on hand with CLI')
@click.option('--file',"-f",metavar='YAML file',prompt='YAML file',show_default=True,required=True, help='YAML file')
def cli(file):
    config = Config(file)

    with Controller(config) as app:

        # app = Controller(config)
        app.prepare_tables()
        app.run()

    # config = Config("mysql.yaml")

    # a = Controller(config)
    # a.test_func()


    