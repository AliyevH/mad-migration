import click
from madmigration.config.conf import Config
from madmigration.main import Controller, NoSQLController
from madmigration.utils.helpers import check_file, file_not_found
import importlib.metadata

__version__ = importlib.metadata.version("madmigration")


@click.group()
def cli():
    """Controller group Cli"""


@cli.command(help="Database Migration tool")

@click.option(
    "--file",
    "-f",
    metavar="YAML",
    required=True,
)

@click.version_option(__version__)

# TODO validate yaml file if given file is correct, drop fk.
def cli(file):

    if check_file(file):
        config = Config(file)

        if config.destination_mongo:
            nosql = NoSQLController(config)
            nosql.run_table_migrations()
        else:
            with Controller(config) as app:
                app.run_table_migrations()
                app.run()
    else:
        file_not_found(file)

