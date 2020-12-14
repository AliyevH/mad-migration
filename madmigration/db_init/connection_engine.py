from sqlalchemy import create_engine, MetaData, event, Table
from sqlalchemy.orm import Session
from sqlalchemy.ext.automap import automap_base
from sqlalchemy_utils.functions.database import database_exists, create_database
import sys
from madmigration.utils.helpers import issue_url,app_name,parse_uri

@event.listens_for(Table, "after_parent_attach")
def before_parent_attach(target, parent):
    if not target.primary_key and "id" in target.c:
        print(target)



class SourceDB:
    def __init__(self, config):
        self.base = automap_base()
        if not database_exists(config.source_uri):

            sys.stdout.write(self.database_not_exists(config.source_uri))
            sys.exit(0)

        self.engine = create_engine(config.source_uri, echo=False)
        self.base.prepare(self.engine, reflect=True)
        self.session = Session(self.engine, autocommit=False, autoflush=False)

    def database_not_exists(self,database):
        
        """This function will be executed if there is no database exists """

        database = parse_uri(database)

        usage = [
            "",
            f"😭 Error: Source database '{database}'  does not exists",
            "",
            f"Run '{app_name()} --help' for usage.",
            "",
            f"🥳  if you think something is wrong please feel free to open issues 👉'{issue_url()}'👈 ",
            "",
            "Exiting ...",
            ""
        ]
        return "\n".join(usage)

class DestinationDB:
    def __init__(self, config):
        self.base = automap_base()
        if not database_exists(config.destination_uri):
            database_name = parse_uri(config.destination_uri)
           
            msg = input(f"The database {database_name} does not exists, would you like to create it in the destination?(y/n) ")
            if msg.lower() == "y":
                try:
                    create_database(config.destination_uri)
                    sys.stdout.write("Database created ..")
                except Exception as err:
                    print(err)
                    sys.exit(1)
            else:
                sys.exit(0)
        self.engine = create_engine(config.destination_uri)
        self.base.prepare(self.engine, reflect=True)
        self.session = Session(self.engine, autocommit=False, autoflush=False)
