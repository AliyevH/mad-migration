from config.conf import config
from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from sqlalchemy.ext.automap import automap_base


class SourceDB():
    def __init__(self):
        self.base = automap_base()
        self.engine = create_engine(config.source_uri)
        self.base.prepare(self.engine, reflect=True)
        self.session = Session(self.engine, autocommit=False, autoflush=False)


class DestinationDB():
    def __init__(self):
        self.base = automap_base()
        self.engine = create_engine(config.destination_uri)
        self.base.prepare(self.engine, reflect=True)
        self.session = Session(self.engine, autocommit=False, autoflush=False)
