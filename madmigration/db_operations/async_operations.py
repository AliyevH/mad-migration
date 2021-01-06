import asyncio
import logging

import gino

from gino.schema import DropConstraint, DropTable
from sqlalchemy import ForeignKeyConstraint, Table
from sqlalchemy.engine import reflection

from alembic.migration import MigrationContext
from alembic.operations import Operations

logger = logging.getLogger(__name__)


class AsyncDbOperations:
    def __init__(self, engine):
        self.engine = engine
        self.metadata = gino.Gino()
        self.loop = asyncio.get_event_loop()

    async def create_table(self, table_name: str, *columns) -> bool:
        """ create a new table """
        try:
            table = Table(table_name, self.metadata, *columns)

            # the gino object comes from "metadata" included in the Table class. metadata is
            # a gino.Gino object which is why table.gino is possible
            await table.gino.create(self.engine, checkfirst=True)

            logger.info("%s is created", table_name)
            return True
        except Exception as err:
            logger.error("_create_table [error] -> %s", err)
            return False
