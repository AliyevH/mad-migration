from madmigration.config.config_schema import MigrationTablesSchema
from madmigration.config.config_schema import ColumnParametersSchema
from madmigration.config.config_schema import TablesInfo
from sqlalchemy import Column, Table, MetaData, ForeignKey,ForeignKeyConstraint
from sqlalchemy.schema import DropConstraint, DropTable
from sqlalchemy.ext.declarative import declarative_base
from alembic.migration import MigrationContext
from sqlalchemy.engine import reflection
from alembic.operations import Operations
from sqlalchemy.dialects.mysql import (
    VARCHAR,
    INTEGER,
    NVARCHAR,
    SMALLINT,
    SET,
    BIGINT,
    BINARY,
    BOOLEAN,
    CHAR,
    DATE,
    DATETIME,
    DECIMAL,
    ENUM,
    FLOAT,
    JSON,
    NUMERIC,
    TEXT,
)
from alembic import op


class Migrate: 
    # keep all tables for deleting on problem, or create all tables in end
    tables = []
    
    #for table foreign keys,collect all fk options ti this list
    fk_constraints = []


    def __init__(self, migration_table: TablesInfo, engine):
        self.sourceDB = engine
        self.migration_tables = migration_table
        self.engine = engine
        self.__queue  = []
        self.metadata = MetaData()
        self.parse_migration_tables()

    def parse_migration_tables(self):
        """
        This function parses migrationTables from yaml file
        """
        self.source_table = self.migration_tables.SourceTable
        self.destination_table = self.migration_tables.DestinationTable
        self.columns = self.migration_tables.MigrationColumns

    def parse_migration_columns(self, migration_columns: ColumnParametersSchema):
        """
        This function parses migrationColumns from yaml file
        """
        self.source_column = migration_columns.sourceColumn
        self.destination_column = migration_columns.destinationColumn
        self.dest_options = migration_columns.destinationColumn.options.dict()

    def create_tables(self):
        """
        Create and check existing tables. 
        Collect foreign key constraints
        """

        tablename = self.destination_table.get("name")
        temp_columns = []
        for column in self.columns:
            self.parse_migration_columns(column)
            fk_key_options = self.dest_options.pop("foreign_key")
            column_type = Migrate.get_column_type( 
                self.dest_options.pop("type_cast")
            )
            if fk_key_options:
                fk_key_options["source_table"] = tablename
                fk_key_options["dest_column"] = self.destination_column.name
                Migrate.fk_constraints.append(fk_key_options)

            type_length = self.dest_options.pop("length")
            if type_length:
                column_type = column_type(type_length)
                    
            col = Column(
                self.destination_column.name,
                column_type,
                **self.dest_options
            )
            
            temp_columns.append(col)
        
        self.__create_table(tablename, *temp_columns)

    # def create_foreign_key(self,options:dict) -> str:
    #     fk_name = f'{options.pop("table_name")}.{options.pop("column_name")}'
    #     return fk_name

    def __create_table(self,table_name:str,*columns) -> bool:
        try:
            conn = self.engine.connect()

            #context config for alembic
            ctx = MigrationContext.configure(conn)
            op = Operations(ctx)
            op.create_table(
                table_name,
                *columns,
            )
            return True 
        except Exception as err:
            print("__create_table -> ", err)
        # finally:
        #     conn.close()

    def check_table(self,table_name: str) -> bool:
        return self.engine.dialect.has_table(self.engine.connect(),table_name)

        
    def get_table_attribute_from_base_class(self, source_table_name: str):
        """
        This function gets table name attribute from sourceDB.base.classes. Example sourceDB.base.class.(table name)
        Using this attribute we can query table using sourceDB.session
        :return table attribute
        """
        # for i in dir(self.sourceDB.base.classes):
        #     print(i)

        # print(" ---------- ")

        return getattr(self.sourceDB.base.classes, source_table_name)

    def get_data_from_source_table(self, source_table_name: str, source_columns: list):

        table = self.get_table_attribute_from_base_class(source_table_name.get("name"))

        rows = self.sourceDB.session.query(table).yield_per(1)

        for row in rows:
            data = {}
            for column in source_columns:
                data[column] = getattr(row, column)
            yield data







    @staticmethod
    def create_fk_constraint(engine:object) -> bool:
        """ Get list of foreign keys from static list `fk_constraints` and created it  """
        try:
            conn = engine.connect()
            ctx = MigrationContext.configure(conn)
            op = Operations(ctx)
            for constraint in Migrate.fk_constraints:
                dest_table_name = constraint.pop("table_name")
                column_name = constraint.pop("column_name")
                source_table = constraint.pop("source_table")
                dest_column = constraint.pop("dest_column")
                print("constraint -> ", constraint)
                op.create_foreign_key(None, source_table, dest_table_name, [dest_column], [column_name], **constraint)
            return True 
        except Exception as err:
            print(err)
            return False
        # finally:
        #     conn.close()

    def add_column(self,table_name:str,column) -> bool:
        try:
            conn = self.engine.connect()
            ctx = MigrationContext.configure(conn)
            op = Operations(ctx)

            op.add_column(
                table_name,column
            )
            return True
        except Exception as err:
            print(err)
            return False
        # finally:
        #     conn.close()

    def check_column(self,table_name:str, column_name: str,column: Column) -> bool:
        """
            Check column exist in destination table or not
            param:: column_name -> is destination column name
        """
        insp = reflection.Inspector.from_engine(self.engine)
        has_column = False
        for col in insp.get_columns(table_name):
            if column_name not in col['name']:
                continue
            has_column = True
        if not has_column:
            while True:
                res = input(f"{column_name} this column does not exist in table {table_name}, add this column to table?(y/n) ")
                if res.lower() == "y":
                    self.add_column(table_name,column)
                    return True
                elif res.lower() == "n":
                    return False
                else:
                    continue
        return has_column

    def db_drop_everything(self,engine):
        # From http://www.sqlalchemy.org/trac/wiki/UsageRecipes/DropEverything
        try:
            conn = engine.connect()

            transactional = conn.begin()

            inspector = reflection.Inspector.from_engine(engine)

            metadata = MetaData()

            tables = []
            all_foreign_keys = []

            for table_name in inspector.get_table_names():
                fks = []
                for fk in inspector.get_foreign_keys(table_name):
                    if not fk["name"]:
                        continue
                    fks.append(ForeignKeyConstraint((), (), name=fk["name"]))
                t = Table(table_name, metadata, *fks)
                tables.append(t)
                all_foreign_keys.extend(fks)

            for foreignkey in all_foreign_keys:
                conn.execute(DropConstraint(foreignkey))

            for table in tables:
                conn.execute(DropTable(table))

            transactional.commit()
        except Exception as err:
            print(err)
            return False
        # finally:
        #     conn.close()     


    @staticmethod
    def get_column_type(type_name: str) -> object:
        """Get class of db type
        :param type_name: str
        :return: object class
        """
        return {
            "string": VARCHAR,
            "varchar": VARCHAR,
            "integer": INTEGER,
            "nvarchar": NVARCHAR,
            "smallint": SMALLINT,
            "set": SET,
            "bigint": BIGINT,
            "binary": BINARY,
            "boolean": BOOLEAN,
            "bool": BOOLEAN,
            "char": CHAR,
            "date": DATE,
            "datetime": DATETIME,
            "decimal": DECIMAL,
            "enum": ENUM,
            "float": FLOAT,
            "json": JSON,
            "numeric": NUMERIC,
            "text": TEXT,
        }.get(type_name.lower())

