from madmigration.db_operations.operations import DBOperations
from madmigration.utils.logger import configure_logging
from sqlalchemy import text

logger = configure_logging(__file__)

class PostgresqlFullMigration:
    def __init__(self, source_db_operations: DBOperations, destination_db_operations: DBOperations):
        self.source_db_operations = source_db_operations
        self.destination_db_operations = destination_db_operations
        self.EXCLUDED_SCHEMAS = ['pg_catalog', 'information_schema']

    def run(self):
        self.collect_all_schemas_from_source_database()
        self.clone_database()
        # self.drop_all_tables_constraints_in_destination_db()
        self.migrate_all_stored_functions_and_procedures_from_source_db_to_destination_db()
        self.migrate_foreign_data_wrapper_and_servers_from_source_to_db()
        self.migrate_user_mappings()
        self.migrate_foreign_tables()

        # self.copy_data_from_source_to_destination()
        # self.set_foreign_key_constraints_in_destination_db()


    def collect_all_schemas_from_source_database(self):
        self.schemas = self.source_db_operations.get_all_schemas()
        # self.schemas = ['_common']

    def clone_database(self):
        for schema in self.schemas:
            if schema in self.EXCLUDED_SCHEMAS:
                continue
            logger.info(f'Creating schema {schema}...')
            self.destination_db_operations.create_schema(schema)
            source_db_metadata = self.source_db_operations.get_reflected_metadata_of_schema(schema=schema)
            self.destination_db_operations.create_all_tables_with_metadata(source_db_metadata)

    def drop_all_tables_constraints_in_destination_db(self):
        for schema in self.schemas:
            if schema in self.EXCLUDED_SCHEMAS:
                continue

            tables = self.destination_db_operations.get_all_tables(schema=schema)
        
            for table in tables:
                fks = self.destination_db_operations.get_foreign_keys_constraints(table.name, schema=schema)
                if not fks:
                    logger.info(f'Foreign Key not found for table {table} in schema {schema}')
                    continue
                for fk in fks:
                    logger.info(f'Dropping foreign key constraint. schema: {schema} table: {table.name} fk: {fk["name"]}')
                    self.destination_db_operations.drop_constraint(fk['name'], table.name, 'foreignkey', schema=schema)

    def copy_data_from_source_to_destination(self):
        for schema in self.schemas:
            if schema in self.EXCLUDED_SCHEMAS:
                continue
        
            tables = self.source_db_operations.get_all_tables(schema=schema)

            for table in tables:
                logger.info(f'Copying data schema: {schema} table: {table}')
                yield_data = self.source_db_operations.query_data_from_table(table)
                for data in yield_data:
                    self.destination_db_operations.insert_data(table_name=table.fullname, data=data._asdict(), schema=schema)

    def __set_foreign_key_constraints_in_destination_table(self, table, schema):
        fks = self.source_db_operations.get_foreign_keys_constraints(table_name=table, schema=schema)
        if not fks:
            logger.info(f'Foreign key constraint not found for table {table} in source database. Skipping...')
            return

        for fk in fks:
            logger.info(f'Setting foreign key constraint in table {table.name}')
            self.destination_db_operations.set_foreign_key_constraint(source_table=table.name, fk_options=fk)

    def set_foreign_key_constraints_in_destination_db(self):
        for schema in self.schemas:
            if schema in self.EXCLUDED_SCHEMAS:
                continue

            tables = self.source_db_operations.get_all_tables(schema=schema)
            for table in tables:
                self.__set_foreign_key_constraints_in_destination_table(table.name, schema)


    def migrate_all_stored_functions_and_procedures_from_source_db_to_destination_db(self):
        functions = self.source_db_operations.get_all_stored_functions_and_procedures()

        for function in functions:
            logger.info(f"Creating stored function {function[1]}")
            self.destination_db_operations.execute_stmt(text(function['definition']))

    def migrate_foreign_data_wrappers(self):
        fdws = self.source_db_operations.get_all_foreign_data_wrappers()
        object_ids = self.source_db_operations.get_object_ids_for_function_names()

        for fdw in fdws:
            fdwname, fdwowner_oid, fdwhandler_oid, fdwvalidator_oid, fdwacl, fdwoptions = fdw
            fdwowner = self.source_db_operations.get_user_name_by_object_id(fdwowner_oid)
            fwdhandler = object_ids.get(fdwhandler_oid)
            fdwvalidator = object_ids.get(fdwvalidator_oid)
            logger.info(f'Creating foreign data wrapper fdw={fdwname} handler={fwdhandler} validator={fdwvalidator}')
            self.destination_db_operations.create_foreign_data_wrapper(foreign_data_wrapper=fdwname, handler=fwdhandler, validator=fdwvalidator)

    def migrate_foreign_servers(self):
        for foreign_data_wrapper, server_name, host, port, dbname in self.source_db_operations.get_fwd_servers_from_pg_database():
            logger.info(f'Creating foreign. server: {server_name} dbname: {dbname} host: {host} port: {port}')
            self.destination_db_operations.create_foreign_server(
                foreign_data_wrapper=foreign_data_wrapper,
                server_name=server_name,
                host=host,
                port=port,
                dbname=dbname
            )

    def migrate_foreign_data_wrapper_and_servers_from_source_to_db(self):
        self.migrate_foreign_data_wrappers()
        self.migrate_foreign_servers()
        

    def migrate_user_mappings(self):
        for server_name, user_name, options in self.source_db_operations.get_user_mappings():
            logger.info(f"Creating user mapping server: {server_name} user: {user_name} options: {options}")
            self.destination_db_operations.create_user_mapping(server_name, user_name, options)

    def __generata_table_structure(self, foreign_table):
        counter = 0
        column_data = ""
        __foreign_table = {}

        for columns in foreign_table:
            foreign_table_name, schema_name, column_name, column_type, ord_number = columns
        
            if ord_number == 1 and counter > 0:
                column_data = column_data.strip(',')
                __foreign_table['column_data'] = column_data
                column_data = ""
                return __foreign_table

            __foreign_table['foreign_table_name'] = foreign_table_name
            __foreign_table['schema_name'] = schema_name
            column_data += column_name + ' ' + column_type + ','

            counter += 1
        else:
            column_data = column_data.strip(',')
            __foreign_table['column_data'] = column_data
            return __foreign_table


    def migrate_foreign_tables(self):
        foreign_tables_list = self.source_db_operations.get_all_foreign_tables()
        
        for foreign_table in foreign_tables_list:
            table_data = self.source_db_operations.get_foreign_table_column_informations(foreign_table_name=foreign_table)
            foreign_table_structure = self.__generata_table_structure(table_data)
            server_name = self.source_db_operations.get_server_name_of_foreign_table(schema_name=foreign_table_structure['schema_name'], table_name=foreign_table_structure['foreign_table_name'])

            self.destination_db_operations.create_foreign_table(
                schema_name=foreign_table_structure['schema_name'],
                table_name=foreign_table_structure['foreign_table_name'],
                column_data=foreign_table_structure['column_data'],
                server_name=server_name
            )
