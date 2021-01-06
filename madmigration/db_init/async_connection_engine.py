import asyncio

import gino
from sqlalchemy import event, Table
from sqlalchemy.ext.automap import automap_base
from sqlalchemy import create_engine

from madmigration.db_init.connection_engine import DestinationDB
from madmigration.utils.helpers import (
    database_not_exists,
    goodby_message,
    aio_database_exists,
    run_await_funtion
)


@event.listens_for(Table, "after_parent_attach")
def before_parent_attach(target, parent):
    if not target.primary_key and "id" in target.c:
        print(target)


class AsyncSourceDB:
    def __init__(self, source_uri):
        if not aio_database_exists(source_uri):
            goodby_message(database_not_exists(source_uri), 0)

        metadata = gino.Gino()
        self.base = automap_base(metadata=metadata)
        self.engine = create_engine(source_uri)
        self.base.prepare()


class AsyncDestinationDB(DestinationDB):
    def __init__(self, destination_uri):
        self.check_for_or_create_database(destination_uri, check_for_database=aio_database_exists)
        self.engine = create_engine(destination_uri, strategy='gino')


@run_await_funtion()
async def create_engine(*args, **kwargs):
    return await gino.create_engine(*args, **kwargs)
