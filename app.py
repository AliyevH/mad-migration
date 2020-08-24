from madmigration.config.conf import config
from madmigration.main import Controller


from sqlalchemy import Table, event

if __name__ == "__main__":

    with Controller(config) as app:

        # app = Controller(config)
        app.prepare_tables()

        # app.run()



