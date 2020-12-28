import logging

from sqlalchemy.schema import DropConstraint, DropTable
from sqlalchemy import MetaData, ForeignKeyConstraint, Table
from alembic.migration import MigrationContext
from sqlalchemy.engine import reflection
from alembic.operations import Operations
from alembic import op

logger = logging.getLogger(__name__)


class DbOperations:
    def __init__(self,engine):
        self.engine = engine
        self.metadata = MetaData()

    def drop_table(self, table_name):
        """ Drop table with given name """
        try:
            conn = self.engine.connect()
            # context config for alembic
            ctx = MigrationContext.configure(conn)
            op = Operations(ctx)
            op.drop_table(table_name)
            logger.info(f"Table {table_name} dropped")
            return True
        except Exception as err:
            logger.error("drop_tables [error] -> %s" % err)
            return False
        finally:
            logger.info("Session closed")
            conn.close()


    def bulk_drop_tables(self, *table_name):
        """ Drop table with given name """
        try:
            for tb in table_name:
                self.drop_table(tb)
            return True
        except Exception as err:
            logger.error("bulk_drop_tables [error] -> %s" % err)

    def update_column(self,table_name, column_name, col_type, **options):
        """ Updated existing table column with new column """
        try:
            conn = self.engine.connect()
            ctx = MigrationContext.configure(conn)
            op = Operations(ctx)

            # op.alter_column(table_name, column_name,type_=col_type,postgresql_using=f"{column_name}::{col_type}") #FIXME not working
        except Exception as err:
            logger.error("update_column [error] -> %s" % err)
        finally:
            conn.close()

    def create_table(self, table_name: str, *columns) -> bool:
        """ create prepared table with alembic """
        try:
            table = Table(table_name,self.metadata, *columns)
            table.create(self.engine, checkfirst=True)
            # conn = self.engine.connect()

            # # context config for alembic
            # ctx = MigrationContext.configure(conn)
            # op = Operations(ctx)
            # op.create_table(
            #     table_name, *columns,
            # )
            logger.info("%s is created" % table_name)
            return True
        except Exception as err:
            logger.error("_create_table [error] -> %s" % err)
            return False

    def add_column(self, table_name: str, *column) -> bool:
        """ Add column to given table """
        try:
            conn = self.engine.connect()
            ctx = MigrationContext.configure(conn)
            op = Operations(ctx)
            for col in column:
                op.add_column(table_name, col)
            return True
        except Exception as err:
            logger.error("add_column [error] -> %s" % err)
            return False
        finally:
            conn.close()

    def create_fk_constraint(self,fk_constraints:list,const_columns:dict) -> bool:
        """ Get list of foreign keys from static list `fk_constraints` and created it  """
        try:
            conn = self.engine.connect()
            ctx = MigrationContext.configure(conn)
            op = Operations(ctx)
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
            return True
        except Exception as err:
            logger.error("create_fk_constraint [error] -> %s" % err)
            return False
        finally:
            conn.close()

    def drop_fk(self, fk_constraints: str):
        try:
            conn = self.engine.connect()
            transactional = conn.begin()
            
            for fk in fk_constraints:
                conn.execute(DropConstraint(fk,cascade=True)) # maybe set cascade=True in future

            transactional.commit()
            return True 
        except Exception as err:
            logger.error("fk_drop [error] -> %s" % err)
            return False
        finally:
            conn.close()
    
    def db_drop_everything(self,table_list):
        """ From http://www.sqlalchemy.org/trac/wiki/UsageRecipes/DropEverything """
        try:
            logger.warning("SIGNAL DROP -> %s" % table_list)
            conn = self.engine.connect()
            transactional = conn.begin()
            inspector = reflection.Inspector.from_engine(self.engine)

            tables = []
            all_foreign_keys = []

            for table_name in inspector.get_table_names():
                if table_name in table_list:
                    fks = []
                    for fk in inspector.get_foreign_keys(table_name):
                        if not fk["name"]:
                            continue
                        fks.append(ForeignKeyConstraint((), (), name=fk["name"]))
                    t = Table(table_name, self.metadata, *fks)
                    tables.append(t)
                    all_foreign_keys.extend(fks)

            for foreignkey in all_foreign_keys:
                conn.execute(DropConstraint(foreignkey))

            for table in tables:
                conn.execute(DropTable(table))

            transactional.commit()
            return True 
        except Exception as err:
            logger.error("db_drop_everything [error] -> %s" % err)
            return False
        finally:
            conn.close()

