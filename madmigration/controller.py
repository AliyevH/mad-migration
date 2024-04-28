import signal
import sys

from madmigration import basemigration, fullmigration
from madmigration.config.conf import ConfigYamlManager
from madmigration.db_operations.operations import DBOperations
from madmigration.utils.logger import configure_logging

logger = configure_logging(__file__)


class Controller:
    def __init__(self, config: ConfigYamlManager, full_migrate=None):
        self.register_ctrl_C_handler()

        self.full_migrate = full_migrate
        self.config = config
        self.source_db_operations = DBOperations(self.config.source_uri)
        self.destination_db_operations = DBOperations(
            self.config.destination_uri, create_database=True
        )

    def __enter__(self):
        return self

    def __exit__(self, *args):
        self.source_db_operations.session.close()
        self.destination_db_operations.session.close()

    def register_ctrl_C_handler(self):
        logger.info(
            "Registering CTRL_C Handler. In case of termination app will delete everything in destination database"
        )
        signal.signal(signal.SIGINT, self.sig_handler)

    def sig_handler(self, sig_num, _sig_frame):
        logger.warn(f"Terminate app with signal: {sig_num}")
        logger.info("Dropping everything in destination db")
        self.destination_db_operations.db_drop_everything()
        sys.exit(sig_num)

    def get_full_migration_class_with_database_driver_name(selk, driver):
        return {
            # "mysqldb": fullmigration.MysqlFullMigration,
            # "mysql+mysqldb": fullmigration.MysqlFullMigration,
            # "pymysql": fullmigration.MysqlFullMigration,
            # "mysql+pymysql": fullmigration.MysqlFullMigration,
            # "mariadb+pymsql": fullmigration.MysqlFullMigration,
            "psycopg2": fullmigration.PostgresqlFullMigration,
            "pg8000": fullmigration.PostgresqlFullMigration,
        }.get(driver)

    def get_base_migration_class_with_database_driver_name(self, driver):
        return {
            "mysqldb": basemigration.MysqlMigrate,
            "mysql+mysqldb": basemigration.MysqlMigrate,
            "pymysql": basemigration.MysqlMigrate,
            "mysql+pymysql": basemigration.MysqlMigrate,
            "mariadb+pymsql": basemigration.MysqlMigrate,
            "psycopg2": basemigration.PgMigrate,
            "pg8000": basemigration.PgMigrate,
        }.get(driver)

    def run(self):
        self.destination_db_driver_name = self.destination_db_operations.engine.driver

        if self.full_migrate:
            migration = self.get_full_migration_class_with_database_driver_name(
                self.destination_db_driver_name
            )
            mig = migration(self.source_db_operations, self.destination_db_operations)
        else:
            migration = self.get_base_migration_class_with_database_driver_name(
                self.destination_db_driver_name
            )
            mig = migration(
                self.config, self.source_db_operations, self.destination_db_operations
            )

        mig.run()


def run(config_file, full_migrate):
    conf = ConfigYamlManager(config_file)

    with Controller(config=conf, full_migrate=full_migrate) as c:
        c.run()
