from madmigration.scripts.commands import cli
from madmigration.utils.logger import configure_logging

def run():
    configure_logging(__file__)
    cli()
