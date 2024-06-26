import importlib.metadata
import sys
import click

from madmigration.controller import run

__version__ = importlib.metadata.version("madmigration")


@click.group()
def cli():
    """Controller group Cli"""


@cli.command(help="Database Migration tool")
@click.option("--file", "-f", metavar="YAML", required=True)
@click.option("--full-migrate", default=False, required=False)
@click.version_option(__version__)
def cli(file, full_migrate):
    run(config_file=file, full_migrate=full_migrate)


if __name__ == "__main__":
    sys.exit(cli())
