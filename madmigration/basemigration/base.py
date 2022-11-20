import signal
import sys
from queue import Queue

from madmigration.config.config_schema import MigrationTablesSchema
from madmigration.config.config_schema import ColumnParametersSchema
from sqlalchemy import Column, MetaData
from sqlalchemy.engine import reflection
from collections import defaultdict
from madmigration.postgresqldb.type_convert import get_type_object
from madmigration.config.conf import ConfigYamlManager
from madmigration.db_operations.operations import DbOperations
from madmigration.utils.logger import configure_logging


logger = configure_logging(__name__)


class BaseMigrate():
    q = Queue()  # Static queue for fk constraints data
    tables = set()

    def __init__(self, config: ConfigYamlManager, destination_db):
        self.config = config
        self.migration_tables = self.config.migrationTables
        self.engine = destination_db.engine
        self.connection = destination_db
        self.metadata = MetaData()
        self.table_list = set()
        self.table_create = defaultdict(list)
        self.table_update = defaultdict(list)
        self.alter_col = defaultdict(list)
        self.fk_constraints = []
        self.dest_fk = []
        self.contraints_columns = defaultdict(set)
        self.db_operations = DbOperations(self.engine)
        self._drop_tables = []

        signal.signal(signal.SIGINT, self.sig_handler)

    def __enter__(self):
        return self

    def __exit__(self, type, value, traceback):
        self.engine.session.close()

    def sig_handler(self, sig_num, _sig_frame):
        logger.warn("TERMINATE APP WITH SIGNAL -> %d" % sig_num)
        if self.tables:
            self.db_operations.db_drop_everything(self.tables)
        sys.exit(sig_num)

    def collect_table_names(self):
        """Collects all tables that the program should create"""
        self.tables = self.config.collect_destination_tables()

    def parse_migration_tables(self, tabels_schema: MigrationTablesSchema):
        """
        This function parses migrationTables from yaml file
        """
        try:
            self.source_table = tabels_schema.migrationTable.SourceTable.dict()
            self.destination_table = tabels_schema.migrationTable.DestinationTable.dict()
            self.columns = tabels_schema.migrationTable.MigrationColumns
        except Exception as err:
            logger.error("parse_migration_tables [error] -> %s" % err)

    def parse_migration_columns(
        self, tablename: str, migration_columns: ColumnParametersSchema
    ):
        """
        This function parses migrationColumns schema and prepare column
        """
        try:
            table_exists = self.db_operations.is_table_exists(tablename)

            for col in migration_columns:
                self.source_column = col.sourceColumn
                self.destination_column = col.destinationColumn
                self.dest_options = col.destinationColumn.options.dict()

                self._parse_fk(tablename, self.dest_options.pop("foreign_key"))
                column_type = self._parse_column_type()

                col = Column(self.destination_column.name, column_type, **self.dest_options)
                if table_exists:
                    if not self.db_operations.is_column_exists_in_table(tablename, self.destination_column.name):
                        #     self.add_alter_column(tablename, {"column_name": self.destination_column.name,"type":column_type,"options":{**self.dest_options}})
                        # else:
                        self.add_updated_table(tablename, col)
                else:
                    self.add_created_table(tablename, col)
        except Exception as err:
            logger.error("parse_migration_columns [error] -> %s" % err)

    def add_updated_table(self, table_name: str, col: Column):
        self.table_update[table_name].append(col)

    def add_created_table(self, table_name: str, col: Column):
        self.table_create[table_name].append(col)

    def add_alter_column(self, table_name: str, col: Column):
        self.alter_col[table_name].append(col)

    def prepare_tables(self):
        try:
            for migrate_table in self.migration_tables:
                if migrate_table.migrationTable.DestinationTable.create:
                    self.parse_migration_tables(migrate_table)
                    self.parse_migration_columns(self.destination_table.get("name"), self.columns)
        except Exception as err:
            logger.error("prepare_tables  [error] -> %s" % err)

    def update_table(self):

        for tab, col in self.table_update.items():
            self.db_operations.add_column(tab, *col)
        return True

    def alter_columns(self):
        for tab, val in self.alter_col.items():
            for i in val:
                self.db_operations.update_column(tab, i.pop("column_name"), i.pop("type"), **i.pop("options"))
        return True

    def create_tables(self):
        for tab, col in self.table_create.items():
            self.db_operations.create_table(tab, *col)
        return True

    def process(self):
        """
        Create and check existing tables. 
        Collect foreign key constraints
        """
        try:
            self.dest_fk, self.contraints_columns = self.db_operations.collect_fk_and_constraint_columns(self.table_list)
            if self._drop_tables:
                self.db_operations.bulk_drop_tables(*self._drop_tables)
            self.update_table()
            self.create_tables()
            self.db_operations.create_fk_constraint(self.fk_constraints,self.contraints_columns)
            return True
        except Exception as err:
            logger.error("create_tables [error] -> %s" % err)

    def _parse_column_type(self) -> object:
        """ Parse column type and options (length,type and etc.) """

        try:
            column_type = self.get_column_type(self.dest_options.pop("type_cast"))
            type_length = self.dest_options.pop("length")
            if type_length:
                column_type = column_type(type_length)
            return column_type
        except Exception as err:
            logger.error("_parse_column_type [error] -> %s" % err)

        # logger.error(self.dest_options.get("length"))
        type_length = self.dest_options.pop("length")
        if type_length:
            column_type = column_type(type_length)
        return column_type

    def _parse_fk(self, tablename, fk_options):
        """ Parse foreignkey and options (use_alter,colum and etc.) """
        try:
            if fk_options:
                fk_options["source_table"] = tablename
                fk_options["dest_column"] = self.destination_column.name
                self.fk_constraints.append(fk_options)
        except Exception as err:
            logger.error("_parse_fk [error] -> %s" % err)

    def get_input(self,table_name):
        while True:
            answ = input(
                f"Table with name '{table_name}' already exist,\
'{table_name}' table will be dropped and recreated,your table data will be lost,process?(y/n) ")
            if answ.lower() == "y":
                if self.dest_fk[table_name]:
                    self.db_operations.drop_fk(self.dest_fk[table_name])
                self._drop_tables.append(table_name)
                return False
            elif answ.lower() == "n":
                return True
            else:
                continue

    def get_table_attribute_from_base_class(self, source_table_name: str):
        """
        This function gets table name attribute from sourceDB.base.classes. Example sourceDB.base.class.(table name)
        Using this attribute we can query table using sourceDB.session
        :return table attribute
        """
        return getattr(self.connection.base.classes, source_table_name)

    def get_data_from_source_table(self, source_table_name: str, source_columns: list):

        table = self.get_table_attribute_from_base_class(source_table_name.name)
        rows = self.connection.session.query(table).yield_per(1)

        for row in rows:
            data = {}
            for column in source_columns:
                data[column] = getattr(row, column)
            yield data

    @staticmethod
    def insert_data(engine, table_name, data: dict):
        # stmt = None
        try:
            stmt = engine.base.metadata.tables[table_name].insert().values(**data)

        except Exception as err:
            logger.error("insert_data stmt [error] -> %s" % err)
            return
        # logger.error("STMT",stmt)

        try:
            engine.session.execute(stmt)
        except Exception as err:
            logger.error("insert_data passing into queue [error] -> %s" % err)
            BaseMigrate.put_queue(stmt)

        try:
            engine.session.commit()
        except Exception as err:
            logger.error("insert_data [error] -> %s" % err)
            engine.session.rollback()
        finally:
            engine.session.close()

    @staticmethod
    def insert_queue(engine):
        for stmt in BaseMigrate.q.queue:

            try:
                logger.info("Inserting from queue")
                engine.session.execute(stmt)
            except Exception as err:
                logger.error("insert_queue [error] -> %s" % err)

            try:
                engine.session.commit()
            except Exception as err:
                logger.error("insert_queue [error] -> %s" % err)
                engine.session.rollback()
            finally:
                engine.session.close()

    @staticmethod
    def put_queue(data):
        BaseMigrate.q.put(data)

    @staticmethod
    def get_queue():
        return BaseMigrate.q.get()

    @staticmethod
    def type_cast(data_from_source, mt, convert_info: dict):
        for columns in mt.migrationTable.MigrationColumns:
            source_column = columns.sourceColumn.name
            destination_column = columns.destinationColumn.name

            if columns.destinationColumn.options.type_cast:
                destination_type_cast = columns.destinationColumn.options.type_cast
            else:
                destination_type_cast = None

            if convert_info.get(destination_column):
                # ClassType is Class of data type (int, str, float, etc...)
                # Using this ClassType we are converting data into format specified in type_cast
                datatype = get_type_object(destination_type_cast)

                try:
                    if datatype == type(data_from_source.get(source_column)):
                        data_from_source[destination_column] = data_from_source.pop(source_column)

                    elif datatype.__name__ == "UUID":
                        data_from_source[destination_column] = str(data_from_source.pop(source_column))
                    else:
                        try:
                            data_from_source[destination_column] = datatype(data_from_source.pop(source_column))
                        except Exception as err:
                            logger.error("type_cast [error] -> %s" % err)
                            data_from_source[destination_column] = None

                except Exception as err:
                    logger.error("type_cast [error] -> %s" % err)
                    data_from_source[destination_column] = None
            else:
                data_from_source[destination_column] = data_from_source.pop(source_column)

        return data_from_source

    @staticmethod
    def get_column_type(type_name: str) -> object:
        """Get class of db type
        :param type_name: str
        :return: object class
        """
        raise NotImplementedError
