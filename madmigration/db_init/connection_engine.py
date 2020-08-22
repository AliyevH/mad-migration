from sqlalchemy import create_engine, MetaData, event, Table
from sqlalchemy.orm import Session
from sqlalchemy.ext.automap import automap_base

from madmigration.config.conf import config


@event.listens_for(Table, "after_parent_attach")
def before_parent_attach(target, parent):
    if not target.primary_key and "id" in target.c:
        engine = create_engine(config.source_uri)
        conn = engine.connect()
        sql_mode = conn.execute("SELECT @@sql_mode").fetchone()[0]
        try:
            conn.execute("SET sql_mode=''")
            conn.execute(f'alter table {target} add primary key(id)')
        except Exception as err:
            print(err)
        finally:
            conn.execute(f"SET sql_mode='{sql_mode}'")
            conn.close()


class SourceDB:
    def __init__(self, config):
        self.base = automap_base()
        self.engine = create_engine(config.source_uri)
        self.base.prepare(self.engine, reflect=True)
        self.session = Session(self.engine, autocommit=False, autoflush=False)


class DestinationDB:
    def __init__(self, config):
        self.base = automap_base()
        self.engine = create_engine(config.destination_uri)
        self.base.prepare(self.engine, reflect=True)
        self.session = Session(self.engine, autocommit=False, autoflush=False)
