import click
from madmigration.config.conf import Config
from madmigration.db_init.connection_utils import ConfigLocation, get_database_connection_object
from madmigration.main import MigrationController
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

    source_db = get_database_connection_object(config.source_uri)
    destination_db = get_database_connection_object(config.destination_uri)

    sourc_conn = source_db(config.source_uri, ConfigLocation.SOURCE)
    destination_conn = destination_db(config.destination_uri, ConfigLocation.DESTINATION)
    try:
        with MigrationController(config=config, source_db=sourc_conn, destination_db=destination_conn) as app:
            app.run_table_migrations()
            app.run()
    except:
        print('failing to migrate')