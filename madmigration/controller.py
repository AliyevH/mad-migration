import sys

from madmigration.config.conf import ConfigYamlManager
from madmigration.db_operations.operations import DBOperations
from madmigration import basemigration, full_migration
from madmigration.utils.logger import configure_logging

logger = configure_logging(__file__)

class Controller:
    def __init__(self, config: ConfigYamlManager):
        self.config = config
        self.source_db_operations = DBOperations(self.config.source_uri)
        self.destination_db_operations = DBOperations(self.config.destination_uri, create_database=True)

    def __enter__(self):
        return self


    def __exit__(self, *args):
        self.source_db_operations.session.close()
        self.destination_db_operations.session.close()


    def sig_handler(self, sig_num, _sig_frame):
        logger.warn(f"Terminate app with signal -> {sig_num}")
        self.destination_db_operations.db_drop_everything()
        sys.exit(sig_num)
        

    def get_base_migration_class_with_database_driver_name(self, driver):
        return {
            "mysqldb": basemigration.MysqlMigrate,
            "mysql+mysqldb": basemigration.MysqlMigrate,
            "pymysql": basemigration.MysqlMigrate,
            "mysql+pymysql": basemigration.MysqlMigrate,
            "mariadb+pymsql": basemigration.MysqlMigrate,
            "psycopg2": basemigration.PgMigrate,
            "pg8000": basemigration.PgMigrate,
            # "pyodbc": MssqlMigrate,
            # "mongodb": MongoDbMigrate
        }.get(driver)

    def run(self):
        self.destination_db_driver_name = self.destination_db_operations.engine.driver
        migration = self.get_base_migration_class_with_database_driver_name(self.destination_db_driver_name)
        mig = migration(self.config, self.source_db_operations, self.destination_db_operations)
        mig.run()


class NoSQLControllerWithYamlConf(Controller):
    pass


class SqlControllerWithYamlConf(Controller):
    def __init__(self, config: ConfigYamlManager):
        super().__init__(config)



class FullMigrateController(Controller):
    def __init__(self, config: ConfigYamlManager):
        super().__init__(config)

    def run():
        pass



def run(config_file, full_migrate):
    conf = ConfigYamlManager(config_file)
    
    if conf.destination_mongo:
        controller = NoSQLControllerWithYamlConf
    elif not conf.destination_mongo:
        controller = SqlControllerWithYamlConf
    elif full_migrate:
        controller = FullMigrateController

    with controller(conf) as c:
        c.run()
