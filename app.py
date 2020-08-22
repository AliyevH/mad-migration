from madmigration.config.conf import config
from madmigration.main import Controller


from sqlalchemy import Table, event

if __name__ == "__main__":
    app = Controller(config)
    app.prepare_tables()
    app.sourceDB.session.close()
    app.destinationDB.session.close()
    # app.run()

