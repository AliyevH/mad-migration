from madmigration.config.config_schema import MigrationTablesSchema
from madmigration.config.config_schema import ColumnParametersSchema
from madmigration.config.config_schema import TablesInfo
from sqlalchemy import Column, Table, MetaData, ForeignKey,ForeignKeyConstraint
from sqlalchemy.schema import DropConstraint, DropTable
from sqlalchemy.ext.declarative import declarative_base
from alembic.migration import MigrationContext
from sqlalchemy.engine import reflection
from alembic.operations import Operations
from sqlalchemy.dialects.postgresql import (
    VARCHAR,
    INTEGER,

    # NVARCHAR,
    SMALLINT,
    # SET,
    BIGINT,
    # BINARY,
    BOOLEAN,
    CHAR,
    DATE,
    # DECIMAL,
    ENUM,
    FLOAT,
    JSON,
    NUMERIC,
    TEXT,
)
from sqlalchemy import DateTime
from sqlalchemy_utils import UUIDType
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
    
    def __enter__(self):
        return self

    def __exit__(self, type, value, traceback):
        self.engine.session.close()
        self.sourceDB.session.close()

    def parse_migration_tables(self):
        """
        This function parses migrationTables from yaml file
        """
        self.source_table = self.migration_tables.SourceTable.dict()
        self.destination_table = self.migration_tables.DestinationTable.dict()
        self.columns = self.migration_tables.MigrationColumns

    def parse_migration_columns(self,tablename:str, migration_columns: ColumnParametersSchema):
        """
        This function parses migrationColumns schema and prepare column
        """
        self.source_column = migration_columns.sourceColumn
        self.destination_column = migration_columns.destinationColumn
        self.dest_options = migration_columns.destinationColumn.options.dict()
        print(self.dest_options)
        if self.check_column(tablename,self.destination_column.name):
            return False
        self._parse_fk(tablename,self.dest_options.pop("foreign_key"))
        column_type = self._parse_column_type()
                
        col = Column(
            self.destination_column.name,
            column_type,
            **self.dest_options
        )
        return col

    def create_tables(self):
        """
        Create and check existing tables. 
        Collect foreign key constraints
        """

        tablename = self.destination_table.get("name")
        update_table = self.check_table(tablename)
    
        temp_columns = []
        for column in self.columns:
            # parse colum and return prepared column
            col = self.parse_migration_columns(tablename,column)
            if col is not False:
                temp_columns.append(col)
        if update_table:
            # if table exist we add column to table
            return self.add_column(tablename,*temp_columns)
        else:
            return self._create_table(tablename, *temp_columns)

    def _parse_column_type(self) -> object:
        """ Parse column type and options (length,type and etc.) """
        column_type = Migrate.get_column_type( 
            self.dest_options.pop("type_cast")
        )
        print(self.dest_options.get("length"))
        type_length = self.dest_options.pop("length")
        if type_length:
            column_type = column_type(type_length)
        return column_type

    def _parse_fk(self,tablename, fk_options):
        """ Parse foreignkey and options (use_alter,colum and etc.) """
        if fk_options:
            fk_options["source_table"] = tablename
            fk_options["dest_column"] = self.destination_column.name
            Migrate.fk_constraints.append(fk_options)

    def _create_table(self,table_name:str,*columns) -> bool:
        """ create prepared table with alembic """
        try:
            conn = self.engine.connect()

            #context config for alembic
            ctx = MigrationContext.configure(conn)
            op = Operations(ctx)
            print(table_name)
            op.create_table(table_name,
            *columns,
            )
            return True 
        except Exception as err:
            print(err)
        finally:
            conn.close()
    
    def update_table(self,table_name,*columns):
        pass

    def check_table(self,table_name: str) -> bool:
        """ Check table exist or not, and wait user input """
        if self.engine.dialect.has_table(self.engine.connect(),table_name):
            while True:
                answ = input(f"Table with name {table_name} already exist, recreate table?(y/n)")
                if answ.lower() == "y":
                    msg = f"The table {table_name} will be dropped and recreated,your table data will be lost,process?(yes/no)"
                    rcv = input(msg)
                    if rcv.lower() == "yes":
                        self.drop_table(table_name)
                        return False
                    elif rcv.lower() == "no":
                        return True
                elif answ.lower() == "n":
                    return True
                else:
                    continue
        return False

    def drop_table(self,table_name):
        """ Drop table with given name """
        try:
            conn = self.engine.connect()

            #context config for alembic
            ctx = MigrationContext.configure(conn)
            op = Operations(ctx)
            print(table_name)
            op.drop_table(table_name)
            return True 
        except Exception as err:
            print(err)
        finally:
            conn.close()
    
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
            print(Migrate.fk_constraints)
            for constraint in Migrate.fk_constraints:
                dest_table_name = constraint.pop("table_name")
                column_name = constraint.pop("column_name")
                source_table = constraint.pop("source_table")
                dest_column = constraint.pop("dest_column")
                # if not self.check_column(dest_table_name,column_name):
                print(constraint)
                op.create_foreign_key(None, source_table, dest_table_name, [dest_column], [column_name], **constraint)
            return True 
        except Exception as err:
            print(err)
            return False
        finally:
            conn.close()

    def add_column(self,table_name:str,*column) -> bool:
        """ Add column to given table """
        try:
            conn = self.engine.connect()
            ctx = MigrationContext.configure(conn)
            op = Operations(ctx)
            for col in column:
                op.add_column(
                    table_name,col
                )
            return True
        except Exception as err:
            print(err)
            return False
        finally:
            conn.close()
    
    def update_column(self,table_name,column_name,**options):
        """ Updated existing table column with new column """
        pass

    def check_column(self,table_name:str, column_name: str) -> bool:
        """
            Check column exist in destination table or not
            param:: column_name -> is destination column name
        """
        try:
            insp = reflection.Inspector.from_engine(self.engine)
            has_column = False
            for col in insp.get_columns(table_name):
                if column_name not in col['name']:
                    continue
                has_column = True
            return has_column
        except: 
            return False
    
    def db_drop_everything(self,engine):
        """ From http://www.sqlalchemy.org/trac/wiki/UsageRecipes/DropEverything """
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
        finally:
            conn.close()     


    @staticmethod
    def get_column_type(type_name: str) -> object:
        """Get class of db type
        :param type_name: str
        :return: object class
        """
        return {
            "varchar": VARCHAR,
            "integer": INTEGER,
            # "nvarchar": NVARCHAR,
            "smallint": SMALLINT,
            # "set": SET,
            "bigint": BIGINT,
            # "binary": BINARY,
            "boolean": BOOLEAN,
            "bool": BOOLEAN,
            "char": CHAR,
            "date": DATE,
            "string": VARCHAR,
            "datetime": DateTime,
            # "decimal": DECIMAL,
            "enum": ENUM,
            "float": FLOAT,
            "json": JSON,
            "numeric": NUMERIC,
            "text": TEXT,
            "uuid": UUIDType
        }.get(type_name.lower())


    
