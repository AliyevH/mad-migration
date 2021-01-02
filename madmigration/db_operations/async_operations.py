import asyncio
import logging

from sqlalchemy.schema import DropConstraint, DropTable
from sqlalchemy import MetaData, ForeignKeyConstraint, Table
from sqlalchemy.engine import reflection

from alembic.migration import MigrationContext
from alembic.operations import Operations

logger = logging.getLogger(__name__)


class AsyncDbOperations:
    def __init__(self, engine):
        self.engine = engine
        self.metadata = MetaData()
        self.loop = asyncio.get_event_loop()

    async def drop_table(self, table_name):
        """ Drop table with given name """
        try:
            conn = await self.engine.connect()

            # context config for alembic
            ctx = MigrationContext.configure(conn)
            op = Operations(ctx)
            op.drop_table(table_name)

            logger.info("Table %s dropped", table_name)
            return True
        except Exception as err:
            logger.error("drop_tables [error] -> %s", err)
            return False
        finally:
            logger.info("Session closed")
            await conn.close()

    async def bulk_drop_tables(self, *table_name):
        """ Drop tables with given name """
        try:
            await asyncio.gather(*[self.drop_table(table) for table in table_name])
            return True
        except Exception as err:
            logger.error("bulk_drop_tables [error] -> %s", err)

    async def create_table(self, table_name: str, *columns) -> bool:
        """ create prepared table with alembic """
        try:
            table = Table(table_name, self.metadata, *columns)
            table.create(self.engine, checkfirst=True)

            logger.info("%s is created", table_name)
            return True
        except Exception as err:
            logger.error("_create_table [error] -> %s", err)
            return False

    async def add_column(self, table_name: str, *column) -> bool:
        """ Add column to given table """
        try:
            conn = await self.engine.connect()
            ctx = MigrationContext.configure(conn)
            op = Operations(ctx)

            # run blocking function cooncurrently in an async executor
            col_list = [
                self.loop.run_in_executor(None, op.add_column, table_name, col) for col in column
            ]
            await asyncio.gather(*col_list)

            return True
        except Exception as err:
            logger.error("add_column [error] -> %s", err)
            return False
        finally:
            await conn.close()

    async def create_fk_constraint(self, fk_constraints: list, const_columns: dict) -> bool:
        """ Get list of foreign keys from static list `fk_constraints` and created it  """
        try:
            conn = await self.engine.connect()

            ctx = MigrationContext.configure(conn)
            op = Operations(ctx)
            for constraint in fk_constraints:
                dest_table_name = constraint.pop("table_name")
                column_name = constraint.pop("column_name")
                source_table = constraint.pop("source_table")
                dest_column = constraint.pop("dest_column")

                if dest_column not in const_columns[source_table]:
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
            logger.error("create_fk_constraint [error] -> %s", err)
            return False

        finally:
            await conn.close()

    async def drop_fk(self, fk_constraints: str):
        try:
            conn = await self.engine.connect()
            transactional = await conn.begin()

            await asyncio.gather(
                *[conn.execute(
                    DropConstraint(fk, cascade=True)
                ) for fk in fk_constraints]
            )

            await transactional.commit()
            return True
        except Exception as err:
            logger.error("fk_drop [error] -> %s", err)
            return False
        finally:
            await conn.close()

    async def db_drop_everything(self, table_list):
        """ From http://www.sqlalchemy.org/trac/wiki/UsageRecipes/DropEverything """
        try:
            logger.warning("SIGNAL DROP -> %s", table_list)
            conn = await self.engine.connect()
            transactional = await conn.begin()
            inspector = reflection.Inspector.from_engine(self.engine)

            tables = []
            all_foreign_keys = []

            for table_name in inspector.get_table_names():
                if table_name in table_list:

                    fks = map(lambda fk: ForeignKeyConstraint((), (), name=fk["name"]) if fk["name"],
                              inspector.get_foreign_keys(table_name))
                    fks = list(fks)

                    t = Table(table_name, self.metadata, *fks)
                    tables.append(t)
                    all_foreign_keys.extend(fks)

            await asyncio.gather(
                *[conn.execute(
                    DropConstraint(foreignkey)
                ) for foreignkey in all_foreign_keys]
            )

            await asyncio.gather(
                *[conn.execute(
                    DropTable(table)
                ) for table in tables]
            )

            await transactional.commit()
            return True
        except Exception as err:
            logger.error("db_drop_everything [error] -> %s", err)
            return False
        finally:
            await conn.close()
