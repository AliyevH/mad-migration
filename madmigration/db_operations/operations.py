import sys
from contextlib import contextmanager
from typing import Optional

from alembic.migration import MigrationContext
from alembic.operations import Operations
from sqlalchemy import (
    ForeignKeyConstraint,
    MetaData,
    Table,
    create_engine,
    inspect,
    text,
)
from sqlalchemy.engine import reflection
from sqlalchemy.engine.url import make_url
from sqlalchemy.exc import NoSuchTableError, ProgrammingError
from sqlalchemy.orm import Session
from sqlalchemy.schema import DropConstraint, DropTable
from sqlalchemy_utils.functions.database import create_database, database_exists

from madmigration.utils.helpers import database_not_exists, goodby_message
from madmigration.utils.logger import configure_logging

logger = configure_logging(__name__)


@contextmanager
def OperationContextManager(engine):
    try:
        conn = engine.connect()
        ctx = MigrationContext.configure(conn)
        op = Operations(ctx)
        yield op
    finally:
        conn.close()


@contextmanager
def InspectorReflection(engine):
    inspector = reflection.Inspector.from_engine(engine)
    yield inspector


class DBOperations:
    def __init__(self, uri, create_database=False):
        try:
            self.uri = uri
            self.password_masked_database_uri = make_url(self.uri)

            if create_database:
                self.create_database_if_not_exists()

            self.engine = create_engine(uri, echo=False)
            self.session = Session(self.engine, autocommit=False, autoflush=False)

            self.metadata = MetaData(bind=self.engine)
            self.metadata.reflect(self.engine)

            self.inspector = reflection.Inspector.from_engine(self.engine)

        except Exception as err:
            logger.error(err)
            sys.exit(1)

    @contextmanager
    def reflected_metadata(self, schema=None):
        if not schema:
            logger.warn(f"Reflecting empty schema {schema}")

        self.metadata.clear()
        self.metadata.reflect(schema=schema)
        yield self.metadata

    def check_if_database_exists(self):
        return True if database_exists(self.uri) else False

    def create_database_if_not_exists(
        self, check_for_database: callable = database_exists
    ):
        if check_for_database(self.uri):
            logger.error(
                "Database exists in destination. Please remove before beginning migration!"
            )
            sys.exit(1)
        else:
            while True:
                msg = input(
                    f"The database {self.password_masked_database_uri} does not exists, would you like to create it in the destination?(y/n) "
                )
                if msg.lower() == "y":
                    try:
                        create_database(self.uri)
                        logger.info(
                            f"Database {self.password_masked_database_uri} created.."
                        )
                        break
                    except Exception:
                        goodby_message(database_not_exists(self.uri), 1)
                elif msg.lower() == "n":
                    goodby_message(
                        "Destination database does not exist \nExiting ...", 0
                    )
                print("Please, select command")

    def drop_table(self, table_name):
        with OperationContextManager(self.engine) as op:
            op.drop_table(table_name)

    def bulk_drop_tables(self, *table_name):
        try:
            for tb in table_name:
                self.drop_table(tb)
            return True
        except Exception as err:
            logger.error(err)
            sys.exit(1)

    def update_column(self, table_name, column_name, col_type, **options):
        with OperationContextManager(self.engine) as op:
            op.alter_column(
                table_name,
                column_name,
                type_=col_type,
                postgresql_using=f"{column_name}::{col_type}",
            )  # FIXME not working

    def create_table(self, table_name: str, *columns) -> bool:
        with OperationContextManager(self.engine) as op:
            op.create_table(table_name, *columns)

    def add_column(self, table_name: str, *column) -> bool:
        with OperationContextManager(self.engine) as op:
            for col in column:
                op.add_column(table_name, col)

    def create_fk_constraint(self, fk_constraints: list, const_columns: dict) -> bool:
        """Get list of foreign keys from static list `fk_constraints` and create it"""
        with OperationContextManager(self.engine) as op:
            for constraint in fk_constraints:
                dest_table_name = constraint.pop("table_name")
                column_name = constraint.pop("column_name")
                source_table = constraint.pop("source_table")
                dest_column = constraint.pop("dest_column")
                temp = [i for i in const_columns[source_table]]

                if dest_column not in temp:
                    op.create_foreign_key(
                        None,
                        source_table,
                        dest_table_name,
                        [dest_column],
                        [column_name],
                        **constraint,
                    )

    def drop_fk(self, fk_constraints):
        with OperationContextManager(self.engine) as op:
            for fk in fk_constraints:
                op.drop_constraint(fk[1], fk[0], type_="foreignkey")

    def db_drop_everything(self):
        """From http://www.sqlalchemy.org/trac/wiki/UsageRecipes/DropEverything"""
        tables = []
        all_foreign_keys = []
        with InspectorReflection(self.engine) as inspector:
            for table_name in inspector.get_table_names():
                fks = []
                for fk in inspector.get_foreign_keys(table_name):
                    if not fk["name"]:
                        continue
                    fks.append(ForeignKeyConstraint((), (), name=fk["name"]))
                t = Table(table_name, self.metadata, *fks)
                tables.append(t)
                all_foreign_keys.extend(fks)

        with self.engine.connect() as conn:
            for foreignkey in all_foreign_keys:
                conn.execute(DropConstraint(foreignkey))

            for table in tables:
                conn.execute(DropTable(table))

    def collect_fk_and_constraint_columns(self, table_list, schema=None):
        """
        Collect foreign key constraints for tables
        """
        dest_fk = {}
        contraints_columns = {}

        with InspectorReflection(self.engine) as inspector:
            try:
                for table_name in inspector.get_table_names(schema=schema):
                    __table = f"{schema}.{table_name}"
                    if __table in table_list:
                        for fk in inspector.get_foreign_keys(table_name):
                            if not fk["name"]:
                                continue
                            dest_fk[fk["referred_table"]].append((__table, fk["name"]))
                            contraints_columns[table_name].append(
                                *fk["constrained_columns"]
                            )
            except Exception as err:
                logger(err)
                sys.exit()

        return dest_fk, contraints_columns

    def is_column_exists_in_table(self, table_name: str, column_name: str) -> bool:
        with InspectorReflection(self.engine) as inspector:
            columns = inspector.get_columns(table_name)
            for col in columns:
                if column_name in col["name"]:
                    return True
            return False

    def is_table_exists(self, table_name: str) -> bool:
        """Check table exist or not"""
        return table_name in self.get_all_tables_names()

    def insert_data(self, table_name, data: dict, schema=None):
        table = self.get_table_attribute_from_base(table_name, schema=schema)
        try:
            stmt = table.insert().values(**data)
        except Exception as err:
            logger.error(f"Failed to generate sql stmt: {err}", exc_info=True)
            sys.exit(1)
        self.execute_stmt(stmt=stmt)

    def execute_stmt(self, stmt, log_stmt_exception: bool = True):
        try:
            with self.engine.connect() as connection:
                return connection.execute(stmt)
        except Exception as err:
            if log_stmt_exception:
                logger.error(f"Failed to execute stmt: {err}")

    def query_data_from_table(self, table_name, yield_per=1):
        return self.session.query(table_name).yield_per(yield_per)

    def get_table_attribute_from_base(self, source_table_name: str, schema=None):
        try:
            with self.reflected_metadata(schema=schema) as metadata:
                return metadata.tables.get(source_table_name)
        except AttributeError as err:
            logger.error(err)
            sys.exit(1)

    def get_all_schemas(self):
        insp = inspect(self.engine)
        return insp.get_schema_names()

    def get_all_tables(self, schema=None) -> Table:
        with self.reflected_metadata(schema=schema) as metadata:
            return list(metadata.tables.values())

    def get_table(self, table_name, schema=None):
        tables = self.get_all_tables(schema=schema)
        __table = f"{schema}.{table_name}"
        try:
            return tables[__table]
        except KeyError as err:
            logger.error(f"Table {table_name} not found", err)

    def get_all_tables_names(self):
        tables = self.get_all_tables()
        return [table for table in tables]

    def get_table_constraints(self, table):
        return table.constraints

    def get_table_columns(self, table):
        return table.columns.values()

    def drop_constraint(
        self, constraint_name, table_name, constraint_type, schema=None
    ):
        with OperationContextManager(self.engine) as op:
            try:
                op.drop_constraint(
                    constraint_name, table_name, type_=constraint_type, schema=schema
                )
            except ProgrammingError as err:
                logger.error(err)

    def get_foreign_keys_constraints(
        self, table_name, schema=None
    ) -> Optional[list[dict]]:
        """
        Collect foreign key constraints for tables
        """
        try:
            with InspectorReflection(self.engine) as inspector:
                return inspector.get_foreign_keys(table_name, schema=schema)
        except NoSuchTableError as err:
            logger.error(
                f"Table {table_name} not found in schema {schema}: {err}", exc_info=True
            )

    def create_all_tables_with_metadata(self, metadata):
        metadata.create_all(bind=self.engine)

    def create_schema(self, schema: str):
        with self.engine.connect() as conn:
            conn.execute(f"CREATE SCHEMA IF NOT EXISTS {schema}")

    def get_reflected_metadata_of_schema(self, schema):
        with self.reflected_metadata(schema=schema) as metadata:
            return metadata

    def set_foreign_key_constraint(self, source_table: str, fk_options: dict):
        """Exmaple of fk_options:
        {'name': 'orders_personid_fkey', 'constrained_columns': ['personid'], 'referred_schema': None, 'referred_table': 'persons', 'referred_columns': ['id'], 'options': {'ondelete': 'CASCADE'}}
        """
        constraint_name = fk_options.get("name")
        destination_table = fk_options.get("referred_table")
        source_columns = fk_options.get("constrained_columns")
        destination_columns = fk_options.get("referred_columns")
        options = fk_options.get("options")
        on_delete = options.get("ondelete")
        on_update = options.get("onupdate")

        with OperationContextManager(self.engine) as op:
            op.create_foreign_key(
                constraint_name=constraint_name,
                source_table=source_table,
                referent_table=destination_table,
                local_cols=source_columns,
                remote_cols=destination_columns,
                onupdate=on_update,
                ondelete=on_delete,
            )

    def get_all_stored_functions_and_procedures(self):
        sql_stmt = """
            select n.nspname as schema_name,
                p.proname as specific_name,
                case p.prokind
                        when 'f' then 'FUNCTION'
                        when 'p' then 'PROCEDURE'
                        when 'a' then 'AGGREGATE'
                        when 'w' then 'WINDOW'
                        end as kind,
                l.lanname as language,
                case when l.lanname = 'internal' then p.prosrc
                        else pg_get_functiondef(p.oid)
                        end as definition,
                pg_get_function_arguments(p.oid) as arguments,
                t.typname as return_type
            from pg_proc p
            left join pg_namespace n on p.pronamespace = n.oid
            left join pg_language l on p.prolang = l.oid
            left join pg_type t on t.oid = p.prorettype
            where n.nspname not in ('pg_catalog', 'information_schema')
            order by schema_name, specific_name;
        """
        return self.execute_stmt(sql_stmt).fetchall()

    def get_fwd_servers_from_pg_database(self):
        stmt = """
        select
            srvname as name,
            srvowner::regrole as owner,
            fdwname as wrapper,
            srvoptions as options
        from pg_foreign_server
        join pg_foreign_data_wrapper w on w.oid = srvfdw;
        """

        result = self.execute_stmt(text(stmt))
        for r in result.fetchall():
            server_name, owner, foreign_data_wrapper, options = r
            __options = {}
            for option in options:
                k, v = option.split("=")
                __options[k] = v

            host, dbname, port = self.parse_foreign_server_options(__options)
            yield foreign_data_wrapper, server_name, host, port, dbname

    def parse_foreign_server_options(self, option):
        """{dbname=slot-weapon,fetch_size=1500000,host=asia-fdw,port=5432}"""
        return option.get("host"), option.get("dbname"), option.get("port")

    def get_user_name_by_object_id(self, user_id):
        statement = f"SELECT usename FROM pg_user where usesysid={user_id};"
        user = self.execute_stmt(stmt=statement)
        if user:
            return user.fetchone()[0]
        return None

    def get_object_ids_for_function_names(self):
        object_ids = {}
        functions_and_procedures = self.get_all_stored_functions_and_procedures()
        for f in functions_and_procedures:
            (
                schema_name,
                function_name,
                kind,
                language,
                defintion,
                function_args,
                return_type,
            ) = f

            statement = (
                "SELECT * FROM pg_get_object_address('function', '{%s}', '{%s}');"
                % (function_name, function_args)
            )
            try:
                object_addresses = self.execute_stmt(
                    statement, log_stmt_exception=False
                ).fetchall()
                for object_address in object_addresses:
                    class_id, object_id, obj_suid = object_address
                    object_ids[object_id] = function_name

            except AttributeError:
                pass
        return object_ids

    def get_all_foreign_data_wrappers(self):
        stmt = "select * from pg_foreign_data_wrapper;"
        return self.execute_stmt(stmt).fetchall()

    def create_foreign_data_wrapper(
        self, foreign_data_wrapper, handler=None, validator=None
    ):
        stmt = f"CREATE FOREIGN DATA WRAPPER {foreign_data_wrapper}"
        if handler:
            stmt += f" HANDLER {handler}"
        if validator:
            stmt += f" VALIDATOR {validator}"
        self.execute_stmt(text(stmt))

    def create_foreign_server(
        self, foreign_data_wrapper, server_name, host, port, dbname
    ):
        stmt = f"CREATE SERVER {server_name} FOREIGN DATA WRAPPER {foreign_data_wrapper} OPTIONS (host '{host}', dbname '{dbname}', port '{port}');"
        self.execute_stmt(text(stmt))

    def get_user_mappings(self):
        stmt = """
        select * from pg_user_mappings;
        """
        result = self.execute_stmt(text(stmt))
        for i in result.fetchall():
            server_name = i[2]
            user_name = i[4]
            options = i[5]
            yield server_name, user_name, options

    def create_user_mapping(self, server_name, user_name, options):
        if options:
            password = options[0].split("=")[1]
            user = options[1].split("=")[0]
            stmt = text(
                f"CREATE USER MAPPING FOR {user_name} SERVER {server_name} OPTIONS (user '{user}', password '{password}');"
            )
        else:
            stmt = text(f"CREATE USER MAPPING FOR {user_name} SERVER {server_name}")

        self.execute_stmt(stmt)

    def get_all_foreign_tables(self):
        stmt = "select foreign_table_name from information_schema.foreign_tables;"
        foreign_tables = []

        for i in self.execute_stmt(stmt):
            foreign_tables.append(i[0])

        return foreign_tables

    def get_foreign_table_column_informations(self, foreign_table_name):
        stmt = f"""
        SELECT cl.relname As table_name, na.nspname As table_schema, att.attname As column_name
            , format_type(ty.oid,att.atttypmod) AS column_type
            , attnum As ordinal_position
            FROM pg_attribute att
            JOIN pg_type ty ON ty.oid=atttypid
            JOIN pg_namespace tn ON tn.oid=ty.typnamespace
            JOIN pg_class cl ON cl.oid=att.attrelid
            JOIN pg_namespace na ON na.oid=cl.relnamespace
            LEFT OUTER JOIN pg_type et ON et.oid=ty.typelem
            LEFT OUTER JOIN pg_attrdef def ON adrelid=att.attrelid AND adnum=att.attnum
            where attnum>0 and cl.relname like '%{foreign_table_name}%'
        """
        return self.execute_stmt(text(stmt)).fetchall()

    def get_server_name_of_foreign_table(self, schema_name, table_name):
        stmt = f"select foreign_server_name from information_schema.foreign_tables where foreign_table_schema='{schema_name}' and foreign_table_name='{table_name}';"
        server_name = self.execute_stmt(text(stmt)).fetchone()
        if server_name:
            return server_name[0]

    def create_foreign_table(self, schema_name, table_name, column_data, server_name):
        stmt = f"""CREATE FOREIGN TABLE {schema_name}.{table_name} (
            {column_data}
        )
        SERVER {server_name};"""
        self.execute_stmt(text(stmt))
