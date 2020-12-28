from madmigration.config.conf import Config
from pymongo import MongoClient
from sqlalchemy.ext.automap import automap_base
from sqlalchemy import create_engine, inspect
from sqlalchemy.orm import Session
from madmigration.errors import TableDoesNotExists
from madmigration.mongodb.type_convert import get_type_object

class MongoDbMigrate:
    
    def __init__(self, config: Config):
        self.config  = config
        self.sourcedb  = self.config.source_uri
        self.destination_db = self.config.destination_uri
        
       
        self.source_db_config()
        self.destination_db_config()
        self.table_list = set()
        self.collect_table_names()
        self.check_tables_existence()
        self.check_concatenate_tables_existence()
        

   
    def __enter__(self):
        return self
    
    def __exit__(self, type, value, traceback):        
        self.sourceDBConfig.session.close() #closing sqlachmy session engine
        self.mongo_client.close()  #closing mongoDB session


    def collect_table_names(self):
        """ Collects table names defined in the YAML """

        self.table_list = {migrate_table.migrationTable.SourceTable.name for migrate_table in self.config.migrationTables}

  
    def check_tables_existence(self):
        """Check if a given table from PostgreSQL does exists"""

        tables = self.get_tables()

        for table in self.table_list:
            if table not in tables:
                raise TableDoesNotExists(f"Exception raised: Given {table} table does not exists, please check your tables")
                
    
    def check_concatenate_tables_existence(self):
        """Get concatenateTables """

        tables = {concatenateTables.destinationColumn.options.concatenateTable  for migrated_columns in  self.config.migrationTables for concatenateTables in migrated_columns.migrationTable.MigrationColumns if concatenateTables.destinationColumn.options.concatenateTable is not None}
        
        if tables:
            self.table_list.update(tables)
            self.check_tables_existence()
        
       

    def get_tables(self):
        """Getting table names for correctness"""

        return inspect(self.sourceDBConfig.engine).get_table_names()



    def source_db_config(self):
        from madmigration.db_init.connection_engine import SourceDB
        
        self.sourceDBConfig = SourceDB(self.sourcedb)


    def extract_data(self):
        """columns converted to dictionary data type """
        current_table = dict()

        for table in self.config.migrationTables:

            source_table = self.source_table_name(table)  
            destination_collection = self.destination_table_name(table)

            COUNT = 0

            columns = len(table.migrationTable.MigrationColumns)
            for migrating_columns in table.migrationTable.MigrationColumns:
               
                tables_info  = migrating_columns.dict()
              
                COUNT +=1

                current_table.update(
                    {
                        "table_name": source_table,
                        tables_info.get("sourceColumn").get("name"): tables_info
                    })
                
                if COUNT == columns:
                    self.destination_table_operations(current_table,destination_collection)
                    current_table ={}
                    
                    continue
 

    def source_table_name(self,table):
        return table.migrationTable.SourceTable.name

    def destination_table_name(self, table):
        return table.migrationTable.DestinationTable.name


    
    def destination_db_config(self):
        '''Destination database mongo initlizing connection'''

        self.mongo_client = MongoClient(self.destination_db)
        self.mongo_DB = self.mongo_client[self.get_mongo_database()]


    def get_mongo_database(self):
        """ Getting database"""
        return self.destination_db.split("/")[-1]


    def get_table_attribute_from_base_class(self, source_table_name: str):
        """
        This function gets table name attribute from sourceDB.base.classes. Example sourceDB.base.class.(table name)
        Using this attribute we can query table using sourceDB.session
        :return table attribute
        """
 
        return getattr (self.sourceDBConfig.base.classes, source_table_name)

    def get_data_from_source_table(self, source_table_name: str, source_columns: list):
        try:

            table = self.get_table_attribute_from_base_class(source_table_name)
            rows = self.sourceDBConfig.session.query(table).yield_per(1)
            
            for row in rows:
                data = {}
                for column in source_columns:
                    data[column] = getattr(row, column)

                    yield data
        except Exception as err:
            print(err)


    def destination_table_operations(self, table_info, destination_collection):
        """Initial work on table information before migrate """
 
        try:
            document = {}
            temp = {}
            columns = []

            source_table = table_info.pop("table_name")

            for key, value in table_info.items():

                if value.get("destinationColumn").get("options").get("concatenateTable"):
                    #TODO burda bize lazim olan conatante table soheti 
                    pass

                else:
                    columns.append(value.get("sourceColumn").get("name"))
                       
                    document.update({
                        value.get("destinationColumn").get("name"): ""})

                    temp.update({
                        value.get("sourceColumn").get("name") +"_type_"+value.get("destinationColumn").get("name"): value.get("destinationColumn").get("options").get("type_cast")})

            for i in self.get_data_from_source_table(source_table,columns):
                if len(i) == len(columns):
                    for key, value in temp.items():
                        key = key.split("_") 

                        
                        result = get_type_object(value)

                        document.update({key[2]: result(str(i.get(key[0])))})
  
                    self.mongo_DB[destination_collection].insert_one(document.copy())
                 
        except Exception as err:
            print(err)

