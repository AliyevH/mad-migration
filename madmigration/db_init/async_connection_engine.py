from sqlalchemy import event, Table
from sqlalchemy.ext.automap import automap_base

from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy.ext.asyncio import AsyncSession

from sqlalchemy_utils.functions.database import database_exists

from madmigration.db_init.connection_engine import DestinationDB
from madmigration.utils.helpers import database_not_exists, goodby_message


@event.listens_for(Table, "after_parent_attach")
def before_parent_attach(target):
    if not target.primary_key and "id" in target.c:
        print(target)


class AsyncSourceDB:
    def __init__(self, source_uri):
        if not database_exists(source_uri):
            goodby_message(database_not_exists(source_uri), 0)
        self.base = automap_base()
        self.engine = create_async_engine(source_uri, echo=False)
        self.base.prepare(self.engine, reflect=True)
        self.session = AsyncSession(self.engine, autocommit=False, autoflush=False)


class AsyncDestinationDB(DestinationDB):
    def __init__(self, destination_uri):
        super().__init__(destination_uri)

        self.base = automap_base()
        self.engine = create_async_engine(destination_uri)
        self.session = AsyncSession(self.engine, autocommit=False, autoflush=False)
