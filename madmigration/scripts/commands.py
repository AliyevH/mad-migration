import click
import math
import random
import time
import sys
from madmigration.config.conf import Config
from madmigration.main import Controller, NoSQLController
from madmigration.utils.helpers import check_file, file_not_found
from madmigration.utils.helpers import __version__


@click.group()
def cli():
    """Controller group Cli"""


@cli.command(help="simple Migrate ready on hand with CLI")
@click.option(
    "--file",
    "-f",
    metavar="YAML file",
    prompt="YAML file",
    show_default=True,
    required=True,
    help="YAML file",
)
@click.version_option(__version__)
def cli(file):

    config = Config(file)

    # source_db = get_database_connection_object(config.source_uri)(config.source_uri, ConfigLocation.SOURCE)
    # destination_db = get_database_connection_object(config.destination_uri)(config.destination_uri, ConfigLocation.DESTINATION)

    if config.destination_mongo:
        nosql = NoSQLController(config)

        nosql.run_table_migrations()

    else:
        with Controller(config) as app:
            app.run_table_migrations()
            app.run()
