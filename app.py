import logging
from madmigration.scripts.commands import cli
from madmigration.utils.logger import configure_logging


logger = logging.getLogger(__file__)


if __name__ == "__main__":
    configure_logging()
    cli()
