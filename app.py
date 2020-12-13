# from madmigration.config.conf import config
from madmigration.main import Controller
from madmigration.scripts.commands import cli

from sqlalchemy import Table, event

if __name__ == "__main__":
    cli()

    # with Controller(config) as app:

    #     # app = Controller(config)
    #     app.prepare_tables()

        # app.run()
