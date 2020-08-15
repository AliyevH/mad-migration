from conf import Config

from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from sqlalchemy.ext.automap import automap_base

config = Config("test.yaml")
print(config)

class SourceDB():
    def __init__(self):
        self.base = automap_base()
        self.engine = create_engine(config.sourceURI)
        self.base.prepare(self.engine, reflect=True)
        self.session = Session(self.engine, autocommit=False, autoflush=False)


class DestinationDB():
    def __init__(self):
        self.base = automap_base()
        self.engine = create_engine(config.destinationURI)
        self.base.prepare(self.engine, reflect=True)
        self.session = Session(self.engine, autocommit=False, autoflush=False)
