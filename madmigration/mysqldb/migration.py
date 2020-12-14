from madmigration.config.config_schema import MigrationTablesSchema
from madmigration.config.config_schema import ColumnParametersSchema
from madmigration.config.config_schema import TablesInfo
from sqlalchemy import Column, Table, MetaData, ForeignKey,ForeignKeyConstraint
from sqlalchemy.schema import DropConstraint, DropTable
from sqlalchemy.ext.declarative import declarative_base
from alembic.migration import MigrationContext
from sqlalchemy.engine import reflection
from alembic.operations import Operations
from madmigration.errors import TableExists
from sqlalchemy import DateTime
from sqlalchemy_utils import UUIDType
from madmigration.mysqldb.type_convert import get_type_object
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
from collections import defaultdict
from madmigration.config.conf import Config
from pprint import pprint


class Migrate: 
    def __init__(self, config: Config,destination_db):
        self.global_config = config
        self.migration_tables = config.migrationTables
        self.engine = destination_db.engine
        self.connection = destination_db
        self.metadata = MetaData()
        self.table_list = set()
        self.tables_must_create = defaultdict(list)
        self.fk_constraints = []
        self.fk_tables = defaultdict(list)
        self.collect_table_names()
        self.collect_drop_fk()
    
    def __enter__(self):
        return self

    def __exit__(self, type, value, traceback):
        self.engine.session.close()

    def collect_table_names(self):
        """ collects all tables that the program should create """
        try:
            for migrate_table in self.migration_tables:
                # pprint(migrate_table.dict().keys())
                
                tabel_name = migrate_table.migrationTable.DestinationTable.name
                self.table_list.add(tabel_name)
                if migrate_table.migrationTable.DestinationTable.create:
                    self.tables_must_create[tabel_name]
        except Exception as err:
            print("err -> ",err)

    def collect_drop_fk(self):
        """ 
        Collect foreign key constraints for tables so 
        that if something goes wrong, delete everything
        """
        try:
            conn = self.engine.connect()
            transactional = conn.begin()
            inspector = reflection.Inspector.from_engine(self.engine)

            for table_name in inspector.get_table_names():
                if table_name in self.table_list:
                    for fk in inspector.get_foreign_keys(table_name):
                        if not fk["name"]:
                            continue
                        self.fk_tables[table_name].append(ForeignKeyConstraint((), (), name=fk["name"]))
            transactional.commit()
        except Exception as err:
            print("err -> ",err)
            return False
        finally:
            conn.close()

    def parse_migration_tables(self,tabels_schema:MigrationTablesSchema):
        """
        This function parses migrationTables from yaml file
        """
        try:
            self.source_table = tabels_schema.migrationTable.SourceTable.dict()
            self.destination_table = tabels_schema.migrationTable.DestinationTable.dict()
            self.columns = tabels_schema.migrationTable.MigrationColumns
        except Exception as err:
            print("err -> ",err)


    def parse_migration_columns(
        self, tablename: str, migration_columns: ColumnParametersSchema
    ):
        """
        This function parses migrationColumns schema and prepare column
        """
        try:
            print("TABLENAME -> ", tablename)
            for col in migration_columns:
                self.source_column = col.sourceColumn
                self.destination_column = col.destinationColumn
                self.dest_options = col.destinationColumn.options.dict()

                if self.check_column(tablename, self.destination_column.name):
                    return False
                self._parse_fk(tablename, self.dest_options.pop("foreign_key"))
                column_type = self._parse_column_type()

                col = Column(self.destination_column.name, column_type, **self.dest_options)

                self.tables_must_create[tablename].append(col)
        except Exception as err:
            print("parse_migration_columns err -> ",err)

    def prepare_tables(self):
        try:
            for migrate_table in self.migration_tables:
                self.parse_migration_tables(migrate_table)
                self.parse_migration_columns(self.destination_table.get("name"),self.columns)
        except Exception as err:
            print("prepare_tables -> ",err)

    def create_tables(self):
        """
        Create and check existing tables. 
        Collect foreign key constraints
        """
        try:
            
            for tablename, columns in self.tables_must_create.items():
                update_table = False
                update_table = self.check_table(tablename)
                if update_table:
                    # if table exist we add column to table
                    self.add_column(tablename, *columns)
                else:
                    self._create_table(tablename, *columns)
            return True
        except Exception as err:
            print("create_tables err -> ", err)

    def _parse_column_type(self) -> object:
        """ Parse column type and options (length,type and etc.) """
        
        try:
            column_type = Migrate.get_column_type(self.dest_options.pop("type_cast"))
            print(self.dest_options.get("length"))
            type_length = self.dest_options.pop("length")
            if type_length:
                column_type = column_type(type_length)
            return column_type
        except Exception as err:
            print(err)
        
        # print(self.dest_options.get("length"))
        type_length = self.dest_options.pop("length")
        if type_length:
            column_type = column_type(type_length)
        return column_type

    def _parse_fk(self, tablename, fk_options):
        """ Parse foreignkey and options (use_alter,colum and etc.) """
        try:
            if fk_options:
                fk_options["source_table"] = tablename
                fk_options["dest_column"] = self.destination_column.name
                self.fk_constraints.append(fk_options)
        except Exception as err:
            print("_parse_fk err -> ", err)

    def _create_table(self, table_name: str, *columns) -> bool:
        """ create prepared table with alembic """
        try:
            conn = self.engine.connect()

            # context config for alembic
            ctx = MigrationContext.configure(conn)
            op = Operations(ctx)
            print(f"{table_name} is created")
            op.create_table(
                table_name, *columns,
            )
            return True
        except Exception as error:
            print("_create_table err ->", error)
            raise TableExists("Exception raised", f"{error}")
        finally:
            conn.close()

    def update_column(self,table_name,column_name,**options):
        """ Updated existing table column with new column """
        pass

    def check_table(self, table_name: str) -> bool:
        """ Check table exist or not, and wait user input """
        try:
            if self.engine.dialect.has_table(self.engine.connect(), table_name):
                while True:
                    answ = input(
                        f"Table with name {table_name} already exist, recreate table?(y/n)"
                    )
                    if answ.lower() == "y":
                        msg = f"The table {table_name} will be dropped and recreated,your table data will be lost,process?(yes/no)"
                        rcv = input(msg)
                        if rcv.lower() == "yes":
                            self.drop_table_and_fk(table_name)
                            return False
                        elif rcv.lower() == "no":
                            return True
                    elif answ.lower() == "n":
                        return True
                    else:
                        continue
            return False
        except Exception as err:
            print(err)
            return False
    
    def drop_tables(self, *table_name):
        """ Drop table with given name """
        try:
            conn = self.engine.connect()

            # context config for alembic
            ctx = MigrationContext.configure(conn)
            op = Operations(ctx)
            print(table_name)
            for tb in table_name:
                op.drop_table(tb)
            return True
        except Exception as err:
            print("drop_tables err -> ",err)
        finally:
            conn.close()
        
    def get_table_attribute_from_base_class(self, source_table_name: str):
        """
        This function gets table name attribute from sourceDB.base.classes. Example sourceDB.base.class.(table name)
        Using this attribute we can query table using sourceDB.session
        :return table attribute
        """
        return getattr(self.connection.base.classes, source_table_name)

    def get_data_from_source_table(self, source_table_name: str, source_columns: list):

        table = self.get_table_attribute_from_base_class(source_table_name.name)
        rows = self.connection.session.query(table).yield_per(1)

        for row in rows:
            data = {}
            for column in source_columns:
                data[column] = getattr(row, column)
            yield data


    def create_fk_constraint(self) -> bool:
        """ Get list of foreign keys from static list `fk_constraints` and created it  """
        try:
            conn = self.engine.connect()
            ctx = MigrationContext.configure(conn)
            op = Operations(ctx)
            print(self.fk_constraints)
            for constraint in self.fk_constraints:
                dest_table_name = constraint.pop("table_name")
                column_name = constraint.pop("column_name")
                source_table = constraint.pop("source_table")
                dest_column = constraint.pop("dest_column")
                op.create_foreign_key(
                    None,
                    source_table,
                    dest_table_name,
                    [dest_column],
                    [column_name],
                    **constraint,
                )
            return True
        except Exception as err:
            print("create_fk_constraint err -> ",err)
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

    def check_column(self, table_name: str, column_name: str) -> bool:
        """
            Check column exist in destination table or not
            param:: column_name -> is destination column name
        """
        try:
            insp = reflection.Inspector.from_engine(self.engine)
            has_column = False
            for col in insp.get_columns(table_name):
                if column_name not in col["name"]:
                    continue
                has_column = True
            return has_column
        except Exception as err:
            print("check_column err -> ",err)
            return False

    def drop_fk(self, fk_constraints: str):
        try:
            conn = self.engine.connect()
            transactional = conn.begin()
            
            for fk in fk_constraints:
                conn.execute(DropConstraint(fk))

            transactional.commit()
        except Exception as err:
            print("fk_drop -> ",err)
        finally:
            conn.close()

    def drop_table_and_fk(self,table_name):
        try:
            for _, constraint in self.fk_tables.items():
                self.drop_fk(constraint)
            self.drop_tables(*[table_name])
            return  True
        except Exception as err:
            print("err -> ",err)
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
    def insert_data(engine, table_name, data: dict):
        try:
            stmt = engine.base.metadata.tables[table_name].insert().values(**data)
            engine.session.execute(stmt)
            engine.session.commit()
        except Exception as err:
            print("err -> ", err, "data: ", data, "table: ", table_name)
        finally:
            engine.session.close()    

    @staticmethod
    def type_cast(data_from_source, mt, convert_info: dict):

        for columns in mt.migrationTable.MigrationColumns:
            source_column = columns.sourceColumn.get("name")
            destination_column = columns.destinationColumn.name
            
            if columns.destinationColumn.options.type_cast:
                destination_type_cast = columns.destinationColumn.options.type_cast
            else:
                destination_type_cast = None

            if convert_info.get(destination_column):
                # ClassType is Class of data type (int, str, float, etc...)
                # Using this ClassType we are converting data into format specified in type_cast
                datatype = get_type_object(destination_type_cast)

                try:
                    if datatype.__name__ == "uuid4":
                        data_from_source[destination_column] = datatype()
                    else:
                        data_from_source[destination_column] = datatype(data_from_source.pop(source_column))
                       
                except Exception as err:
                    print(err)
                    data_from_source[destination_column] = None
            else:
                data_from_source[destination_column] = data_from_source.pop(source_column)
            
        return data_from_source
        

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
            "uuid": UUIDType
        }.get(type_name.lower())

