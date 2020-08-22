from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from sqlalchemy.ext.automap import automap_base
from pprint import pprint


class SourceDB():
    def __init__(self, config):
        self.base = automap_base()
        self.engine = create_engine(config.source_uri,echo=True)
        self.base.prepare(self.engine, reflect=True)
        self.session = Session(self.engine, autocommit=False, autoflush=False)


class DestinationDB():
    def __init__(self, config):
        self.base = automap_base()
        self.engine = create_engine(config.destination_uri)
        self.base.prepare(self.engine, reflect=True)
        self.session = Session(self.engine, autocommit=False, autoflush=False)
