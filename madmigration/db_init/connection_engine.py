from sqlalchemy import create_engine, MetaData, event, Table
from sqlalchemy.orm import Session
from sqlalchemy.ext.automap import automap_base
from sqlalchemy_utils.functions.database import database_exists, create_database
import sys
from madmigration.utils.helpers import issue_url,app_name,parse_uri
from madmigration.utils.helpers import database_not_exists, goodby_message

@event.listens_for(Table, "after_parent_attach")
def before_parent_attach(target, parent):
    if not target.primary_key and "id" in target.c:
        print(target)



class SourceDB:
    def __init__(self, source_uri):
        if not database_exists(source_uri):
            goodby_message(database_not_exists(source_uri), 0)
        self.base = automap_base()
        self.engine = create_engine(source_uri, echo=False)
        self.base.prepare(self.engine, reflect=True)
        self.session = Session(self.engine, autocommit=False, autoflush=False)
        



class DestinationDB:
    
    def __init__(self, destination_uri):
        if not database_exists(destination_uri):
            while True:
                database = parse_uri(destination_uri)
                msg = input(f"The database {database} does not exists, would you like to create it in the destination?(y/n) ")
                if msg.lower() == "y":
                    try:
                        create_database(destination_uri)
                        sys.stdout.write("Database created ..")
                        break
                    except Exception as err:
                        goodby_message(database_not_exists(err), 1)
                    break
                elif msg.lower() == "n":
                    goodby_message("Destination database does not exit \nExiting ..", 0)
                    break
                print("Please, select command")

        
        self.base = automap_base()
        self.engine = create_engine(destination_uri)
        # self.base.prepare(self.engine, reflect=True)
        self.session = Session(self.engine, autocommit=False, autoflush=False)

