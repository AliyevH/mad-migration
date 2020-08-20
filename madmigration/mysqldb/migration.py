from madmigration.config.config_schema import MigrationTablesSchema
from madmigration.config.config_schema import ColumnParametersSchema
from madmigration.config.config_schema import TablesInfo
from sqlalchemy import Column, Table, MetaData, ForeignKey,ForeignKeyConstraint
from sqlalchemy.ext.declarative import declarative_base
from alembic.migration import MigrationContext
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
    
    #for creating tables with orm
    base = declarative_base()
    fk_constraints = []

    def __init__(self, migration_table: TablesInfo,engine):
        self.migration_tables = migration_table
        self.engine = engine
        self.__queue  = []
        self.metadata = MetaData()
        self.parse_migration_tables()
        

    def parse_migration_tables(self):
        self.source_table = self.migration_tables.SourceTable
        self.destination_table = self.migration_tables.DestinationTable
        self.columns = self.migration_tables.MigrationColumns

    def parse_migration_columns(self, migration_columns: ColumnParametersSchema):
        self.source_column = migration_columns.sourceColumn
        self.destination_column = migration_columns.destinationColumn
        self.dest_options = migration_columns.destinationColumn.options.dict()
        # self.source_options = migration_columns.sourceColumn.options

    def create_tables(self):
        # create destination tables with options

        tablename = self.destination_table.get("name")
        temp_columns = []
        # cls = type(tablename,(Migrate.base,),{"__table_args__ " : {"extend_existing": True},"__tablename__": tablename})

        for column in self.columns:
            self.parse_migration_columns(column)
            fk_key_options = self.dest_options.pop("foreign_key")
            column_type = Migrate.get_column_type(  #TODO column_type foreign_key ola biler
                self.dest_options.pop("type")
            )
            if fk_key_options:
                fk_key_options["source_table"] = tablename
                Migrate.fk_constraints.append(fk_key_options)
                
                
            type_length = self.dest_options.pop("length")
            if type_length:
                column_type = column_type(type_length)
            self.dest_options.pop("type_cast")
            col = Column(
                    column_type,
                    **self.dest_options
                )

            col = Column(
                self.destination_column.name,
                column_type,
                **self.dest_options
            )
            temp_columns.append(col)
        
        print(self.__create_table(tablename, *temp_columns))

    def create_foreign_key(self,options:dict) -> str:
        fk_name = f'{options.pop("table_name")}.{options.pop("column_name")}'
        return fk_name

    def __create_table(self,table_name,*columns):
        try:
            conn = self.engine.connect()
            ctx = MigrationContext.configure(conn)
            op = Operations(ctx)

            op.create_table(table_name,
            *columns,
            )
            return True 
        except Exception as err:
            print(err)
        finally:
            conn.close()

    @staticmethod
    def create_fk_constraint(engine):
        """ Get list of foreign key  """
        try:
            conn = engine.connect()
            ctx = MigrationContext.configure(conn)
            op = Operations(ctx)
            for constraint in Migrate.fk_constraints:
                dest_table_name = constraint.pop("table_name")
                column_name = constraint.pop("column_name")
                source_table = constraint.pop("source_table")
                op.create_foreign_key(None, source_table, dest_table_name, [column_name], [column_name], **constraint)
            return True 
        except Exception as err:
            print(err)
        finally:
            conn.close()


    ###########################
    # Get class of db type #
    ###########################
    @staticmethod
    def get_column_type(type_name: str) -> object:
        """
        :param type_name: str
        :return: object class
        """
        return {
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


    