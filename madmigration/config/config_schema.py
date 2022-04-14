from pydantic import BaseModel, validator
from typing import Optional, Union, List, Any, AnyStr, Dict


class Relationship(BaseModel):
    use_alter: bool = True
    table_name: str
    column_name: str
    ondelete: str = "CASCADE"
    onupdate: str = "NO ACTION"


###########################################
######## GENERAL Grouping #################
###########################################
class DBConfigSchema(BaseModel):
    dbURI: str

    # @validator("type_cast")   #TODO check types
    # def validate_uri(cls,v,values):
    #     if v == "integer" and values["length"] != None:
    #         raise ValueError(f"Type {v} has no length")
    #     return v


class SourceColumn(BaseModel):
    name: str
    

class SourceTableSchema(BaseModel):
    name: str


class DestTableSchema(BaseModel):
    name: str
    create: bool = False


class DatabaseConfig(BaseModel):
    SourceConfig: DBConfigSchema
    DestinationConfig: DBConfigSchema


##############################################
########### SQL GROUPINGS ####################
##############################################
class SQLOptionsSchema(BaseModel):
    primary_key: bool = False
    nullable: bool = False
    default: Any = None
    index: Union[bool, None] = None
    unique: Union[bool, None] = None
    autoincrement: bool = False
    foreign_key: Optional[Relationship] = None
    length: Union[int, None] = None
    type_cast: Union[str, None] = None


class DestinationColumn(BaseModel):
    name: str
    options: SQLOptionsSchema


class SQLColumnMigration(BaseModel):
    sourceColumn: SourceColumn
    destinationColumn: DestinationColumn


class SQLTableInfoSchema(BaseModel):
    SourceTable: SourceTableSchema
    DestinationTable: DestTableSchema
    MigrationColumns: List[SQLColumnMigration]


class SQLConfigSchema(BaseModel):
    Config: DatabaseConfig
    migrationTables: List[SQLTableInfoSchema]
    version: float


##############################################
########### NoSQL GROUPINGS ##################
##############################################
class NoSQLOptionsSchema(BaseModel):
    primary_key: bool = False
    nullable: bool = False
    default: Any = None
    index: Union[bool, None] = None
    unique: Union[bool, None] = None


class NoSQLDestinationColumn(BaseModel):
    name: str
    options: NoSQLOptionsSchema


class NoSQLColumnMigration(BaseModel):
    sourceColumn: SourceColumn
    destinationColumn: NoSQLDestinationColumn


class NoSQLTableInfoSchema(BaseModel):
    SourceTable: SourceTableSchema
    DestinationTable: DestTableSchema
    MigrationColumns: List[NoSQLColumnMigration]


class NoSQLConfigSchema(BaseModel):
    Config: DatabaseConfig
    migrationTables: List[NoSQLTableInfoSchema]
    version: float