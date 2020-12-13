from sqlalchemy import create_engine, MetaData, event, Table
from sqlalchemy.orm import Session
from sqlalchemy.ext.automap import automap_base
from sqlalchemy_utils.functions.database import database_exists, create_database
import sys


@event.listens_for(Table, "after_parent_attach")
def before_parent_attach(target, parent):
    if not target.primary_key and "id" in target.c:
        print(target)
        # engine = create_engine(config.source_uri)
        # conn = engine.connect()
        # sql_mode = conn.execute("SELECT @@sql_mode").fetchone()[0]
        # try:
        #     conn.execute("SET sql_mode=''")
        #     conn.execute(f'alter table {target} add primary key(id)')
        # except Exception as err:
        #     print("before_parent_attach -> ", err)
        # finally:
        #     conn.execute(f"SET sql_mode='{sql_mode}'")
        #     conn.close()


class SourceDB:
    def __init__(self, config):
        self.base = automap_base()
        if not database_exists(config.source_uri):
            print("Exiting ..")
            sys.exit(0)
        self.engine = create_engine(config.source_uri, echo=False)
        self.base.prepare(self.engine, reflect=True)
        self.session = Session(self.engine, autocommit=False, autoflush=False)


class DestinationDB:
    def __init__(self, config):
        self.base = automap_base()
        if not database_exists(config.destination_uri):
            msg = input(f"{config.destination_uri} db does not exist, create destination database?(y/n) ")
            if msg.lower() == "y":
                try:
                    create_database(config.destination_uri)
                    print("database creted ..")
                except Exception as err:
                    print(err)
                    sys.exit(1)
            else:
                sys.exit(0)

        self.engine = create_engine(config.destination_uri)
        self.base.prepare(self.engine, reflect=True)
        self.session = Session(self.engine, autocommit=False, autoflush=False)
