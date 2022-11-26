from queue import Queue

from madmigration.db_operations.operations import DBOperations

from sqlalchemy import Column
from collections import defaultdict

from madmigration.config.conf import ConfigYamlManager
from madmigration.utils.logger import configure_logging
from madmigration.utils.helpers import get_type_object


logger = configure_logging(__name__)



class BaseMigrate():
    def __init__(self, config: ConfigYamlManager, source_db_operations: DBOperations, destination_db_operations: DBOperations):
        self.config = config
        self.source_db_operations = source_db_operations
        self.destination_db_operations = destination_db_operations
        self.tables = set()
        self.table_list = set()
        self.table_create = defaultdict(list)
        self.table_update = defaultdict(list)
        self.alter_col = defaultdict(list)
        self.fk_constraints = []
        self.dest_fk = []
        self.contraints_columns = defaultdict(set)
        self._drop_tables = []
        self.collect_table_names()
        self.q = Queue()

    def run(self):
        self.prepare_tables()
        self.process()
        self.start_migration()

    def collect_table_names(self):
        """Collects all tables that the program should create"""
        self.tables = self.config.collect_destination_tables()

    def add_updated_table(self, table_name: str, col: Column):
        self.table_update[table_name].append(col)

    def add_created_table(self, table_name: str, col: Column):
        self.table_create[table_name].append(col)

    def add_alter_column(self, table_name: str, col: Column):
        self.alter_col[table_name].append(col)

    def prepare_tables(self):
        """Prepare tables which needs to create or delete"""
        for migrate_table in self.config.migrationTables:
            if migrate_table.migrationTable.DestinationTable.create:
                source_table, destination_table, columns = self.config.parse_migration_tables(migrate_table.migrationTable)

                table_exists = self.destination_db_operations.is_table_exists(destination_table.name)
                
                for col in columns:
                    destination_column = col.destinationColumn.name
                    dest_options = col.destinationColumn.options.dict()


                    fk_options = dest_options.pop("foreign_key")
                    if fk_options:
                        fk_options["source_table"] = destination_table.name
                        fk_options["dest_column"] = self.destination_column['name']
                        self.fk_constraints.append(fk_options)

                    column_type = self.get_column_type(dest_options.pop("type_cast"))
                    type_length = dest_options.pop("length")

                    if type_length:
                        column_type = column_type(type_length)

                    col = Column(destination_column, column_type, **dest_options)

                    if table_exists:
                        if not self.destination_db_operations.is_column_exists_in_table(destination_table.name, destination_column):
                            self.add_updated_table(destination_table.name, col)
                    else:
                        self.add_created_table(destination_table.name, col)


    def update_table(self):
        for tab, col in self.table_update.items():
            self.destination_db_operations.add_column(tab, *col)

    def alter_columns(self):
        for tab, val in self.alter_col.items():
            for i in val:
                self.destination_db_operations.update_column(tab, i.pop("column_name"), i.pop("type"), **i.pop("options"))

    def create_tables(self):
        for tab, col in self.table_create.items():
            self.destination_db_operations.create_table(tab, *col)


    def process(self):
        try:
            self.dest_fk, self.contraints_columns = self.destination_db_operations.collect_fk_and_constraint_columns(self.table_list)
            
            if self._drop_tables:
                self.destination_db_operations.bulk_drop_tables(*self._drop_tables)

            self.update_table()
            self.create_tables()
            self.alter_columns()
            self.destination_db_operations.create_fk_constraint(self.fk_constraints, self.contraints_columns)
        except Exception as err:
            logger.error(err)

    def start_migration(self):
        for mt in self.config.migrationTables:
            source_table, destination_table, columns = self.config.parse_migration_tables(mt.migrationTable)

             # Dictionary is used to keep data about destination column and type_cast format
            self.convert_info = {}

            # Columns List is used to keep source Columns names
            # We will send table name and source columns list to function "get_data_from_source_table"
            # get_data_from_source_table function will yield data with specified columns from row
            __columns = []

            for column in columns:
                __columns.append(column.sourceColumn.name)

                if column.destinationColumn.options.type_cast:
                    self.convert_info[column.destinationColumn.name] = column.destinationColumn.options.type_cast

            __source_data = self.get_data_from_source_table(source_table.name, __columns)

            for source_data in __source_data:
                try:
                    new_data = self.type_cast(data_from_source=source_data, mt=mt, convert_info=self.convert_info)
                except Exception as err:
                    logger.error(err)

                unsucessfull_stmt = self.destination_db_operations.insert_data(destination_table.name, new_data)
                if unsucessfull_stmt:
                    self.q.put(unsucessfull_stmt)

        self.insert_data_from_queue()
    

    def insert_data_from_queue(self):
        for stmt in self.q.queue:
            print('stmt ->', stmt)
            try:
                logger.info("Inserting from queue")
                self.destination_db_operations.execute_stmt(stmt)
            except Exception as err:
                logger.error(err, exc_info=True)


    def get_data_from_source_table(self, source_table_name: str, source_columns: list):
        table = self.source_db_operations.get_table_attribute_from_base(source_table_name)
        rows = self.source_db_operations.query_data_from_table(table)

        for row in rows:
            data = {}
            for column in source_columns:
                data[column] = getattr(row, column)
            yield data



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
