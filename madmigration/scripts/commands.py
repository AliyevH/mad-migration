import click
import math
import random
import time
import sys
from madmigration.config.conf import  Config
from madmigration.main import Controller
from madmigration.utils.helpers import check_file, file_not_found

@click.group()
def cli():
    """Controller group Cli"""
    

@cli.command(help='simple Migrate ready on hand with CLI')
@click.option('--file',"-f",metavar='YAML file',prompt='YAML file',show_default=True,required=True, help='YAML file')
def cli(file):  

    if check_file(file):
        config = Config(file)

        with Controller(config) as app:

            app.prepare_tables()
            # app.run()
    else:
        file_not_found(file)

    