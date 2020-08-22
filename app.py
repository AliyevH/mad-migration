from madmigration.config.conf import Config
from madmigration.main import Controller

config = Config("test.yaml")

if __name__ == "__main__":
    app = Controller(config)
    app.prepare_tables()
    app.sourceDB.session.close()
    app.destinationDB.session.close()

    app.run()
