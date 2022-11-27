from sqlalchemy import create_engine, event, Table, MetaData, ForeignKeyConstraint
from sqlalchemy.schema import DropConstraint, DropTable
from sqlalchemy.orm import Session
from sqlalchemy.ext.automap import automap_base
from sqlalchemy_utils.functions.database import database_exists, create_database
from sqlalchemy.engine.url import make_url
from sqlalchemy.ext.declarative import declarative_base
from madmigration.utils.logger import configure_logging
from madmigration.utils.helpers import goodby_message, database_not_exists
from alembic.migration import MigrationContext
from sqlalchemy.engine import reflection
from alembic.operations import Operations
from contextlib import contextmanager
import sys

logger = configure_logging(__name__)

 
@contextmanager
def OperationContextManager(engine):
    try:
        conn = engine.connect()
        ctx = MigrationContext.configure(conn)
        op = Operations(ctx)
        yield op
    except Exception as err:
        logger.error("OperationContextManager ->", err)
        sys.exit(1)
    finally:
        conn.close()

@contextmanager
def InspectorReflection(engine):
    try:
        inspector = reflection.Inspector.from_engine(engine)
        yield inspector
    except Exception as err:
        print('err ->', err)
        logger.error('InspectorReflection ->', err, exc_info=True)
        sys.exit(1)


@contextmanager
def Transaction(engine):
    try:
        conn = engine.connect()
        transactional = conn.begin()
        yield transactional
    except Exception as err:
        logger.error('Transaction ->', err)
        sys.exit(1)
    finally:
        conn.close()


class DBOperations:
    def __init__(self, uri, create_database=False):
        try:
            self.uri = uri
            self.password_masked_database_uri = make_url(self.uri)

            self.engine = create_engine(uri, echo=False)
            self.session = Session(self.engine, autocommit=False, autoflush=False)
            
            self.metadata = MetaData(bind=self.engine)

            if create_database:
                self.create_database_if_not_exists()

            self.base = declarative_base()
            self.base.metadata.reflect(self.engine)


        except Exception as err:
            logger.error(err)
            sys.exit(1)

    def check_if_database_exists(self):
        return True if database_exists(self.uri) else False
            
    def create_database_if_not_exists(self, check_for_database: callable = database_exists):
        if not check_for_database(self.uri):
            while True:
                msg = input(f"The database {self.password_masked_database_uri} does not exists, would you like to create it in the destination?(y/n) ")
                if msg.lower() == "y":
                    try:
                        create_database(self.uri)
                        logger.info(f"Database {self.password_masked_database_uri} created..")
                        break
                    except Exception:
                        goodby_message(database_not_exists(self.uri), 1)
                elif msg.lower() == "n":
                    goodby_message("Destination database does not exist \nExiting ...", 0)
                print("Please, select command")

    def drop_table(self, table_name):
        with OperationContextManager(self.engine) as op:
            op.drop_table(table_name)
            logger.info(f"Table {table_name} dropped")


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
            op.alter_column(table_name, column_name,type_=col_type,postgresql_using=f"{column_name}::{col_type}") #FIXME not working

    def create_table(self, table_name: str, *columns) -> bool:
        with OperationContextManager(self.engine) as op:
            op.create_table(table_name, *columns)
            self.refresh_metadata_reflection()

        logger.info(f"Table {table_name} is created")
    
    def refresh_metadata_reflection(self):
        self.base.metadata.reflect(self.engine)


    def add_column(self, table_name: str, *column) -> bool:
        with OperationContextManager(self.engine) as op:
            for col in column:
                op.add_column(table_name, col)
            logger.info(f"Columns {column} added into table {table_name}")


    def create_fk_constraint(self, fk_constraints: list, const_columns: dict) -> bool:
        """ Get list of foreign keys from static list `fk_constraints` and create it  """
        with OperationContextManager(self.engine) as op:
            for constraint in fk_constraints:
                dest_table_name = constraint.pop("table_name")
                column_name = constraint.pop("column_name")
                source_table = constraint.pop("source_table")
                dest_column = constraint.pop("dest_column")
                temp = [i for i in const_columns[source_table]]
                if not dest_column in temp:
                    op.create_foreign_key(
                        None,
                        source_table,
                        dest_table_name,
                        [dest_column],
                        [column_name],
                        **constraint,
                    )

    def drop_fk(self, fk_constraints: str):
        with OperationContextManager(self.engine) as op:
            for fk in fk_constraints:
                op.drop_constraint(fk[1], fk[0], type_="foreignkey")
                logger.info(f"Dropped foreign key constraint {fk}")


    def db_drop_everything(self):
        """ From http://www.sqlalchemy.org/trac/wiki/UsageRecipes/DropEverything """
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

            conn.commit()


    def collect_fk_and_constraint_columns(self, table_list):
        """ 
        Collect foreign key constraints for tables
        """
        dest_fk = []
        contraints_columns = []

        with InspectorReflection(self.engine) as inspector:
            for table_name in inspector.get_table_names():
                if table_name in table_list:
                    for fk in inspector.get_foreign_keys(table_name):
                        if not fk["name"]:
                            continue
                        dest_fk[fk["referred_table"]].append((table_name,fk["name"]))
                        contraints_columns[table_name].add(*fk["constrained_columns"])

        return dest_fk, contraints_columns

    def is_column_exists_in_table(self, table_name: str, column_name: str) -> bool:
        with InspectorReflection(self.engine) as inspector:
            columns = inspector.get_columns(table_name)
            for col in inspector.get_columns(table_name):
                if column_name in col["name"]:
                    return True
            return False

    def is_table_exists(self, table_name: str) -> bool:
        """Check table exist or not"""
        with InspectorReflection(self.engine) as inspector:
            tables = inspector.get_table_names()
            return table_name in tables

    def insert_data(self, table_name, data: dict):
        table = self.get_table_attribute_from_base(table_name)
        
        try:
            logger.info(f"Inserting {data} into table {table}")
            stmt = table.insert().values(**data)

        except Exception as err:
            logger.error(err, exc_info=True)
            sys.exit(1)
        self.execute_stmt(stmt=stmt)


    
    def execute_stmt(self, stmt):
        try:
            with self.engine.connect() as connection:
                connection.execute(stmt)
        except Exception as err:
            logger.error(err)

    def query_data_from_table(self, table_name, yield_per=1):
        return self.session.query(table_name).yield_per(yield_per)


    def get_table_attribute_from_base(self, source_table_name: str):
        """
        This function gets table name attribute from sourceDB.base.classes. Example sourceDB.base.class.(table name)
        Using this attribute we can query table using sourceDB.session
        :return table attribute
        """
        try:
            return self.base.metadata.tables.get(source_table_name)
        except AttributeError as err:
            logger.error(err)
            sys.exit(1)
