import click
from madmigration.controller import run
import importlib.metadata


@click.group()
def cli():
    """Controller group Cli"""


@cli.command(help="Database Migration tool")
@click.option("--file", "-f", metavar="YAML", required=True)
@click.option("--full-migrate", default=False, required=False)
def cli(config_file, full_migrate):
    run(config_file=config_file, full_migrate=full_migrate)
