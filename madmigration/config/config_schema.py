from pydantic import BaseModel, validator
from typing import Union, List, Any, AnyStr, Dict


class ForeignKeySchema(BaseModel):
    use_alter: bool = True
    table_name: str
    column_name: str
    ondelete: str = "CASCADE"

class OptionsSchema(BaseModel):
    primary_key: bool = False
    nullable: bool = False
    default: Any = None
    index: Union[bool,None] = None
    unique: Union[bool,None] = None
    autoincrement: bool = False
    foreign_key: Union[ForeignKeySchema,None] = None
    length: Union[int,None] = None
    type_cast: Union[str,None] = None

    # @validator("type_cast")   #TODO check types
    # def validate_cast(cls,v,values): 
    #     if v == "integer" and values["length"] != None:
    #         raise ValueError(f"Type {v} has no length")
    #     return v


class SourceConfigSchema(BaseModel):
    SourceConfig: Dict[str, str]


class DestinationConfigSchema(BaseModel):
    DestinationConfig: Dict[str, str]


class SourceTableSchema(BaseModel):
    name: str
    

class DestTableSchema(BaseModel):
    name: str
    create: bool = True
class DestinationColumn(BaseModel):
    name: str
    options: OptionsSchema


class ColumnParametersSchema(BaseModel):
    destinationColumn: DestinationColumn
    sourceColumn: Any


class TablesInfo(BaseModel):
    SourceTable: SourceTableSchema
    DestinationTable: DestTableSchema
    MigrationColumns: List[ColumnParametersSchema]


class MigrationTablesSchema(BaseModel):
    migrationTable: TablesInfo


class ConfigSchema(BaseModel):
    Configs: List[Union[SourceConfigSchema, DestinationConfigSchema]]
    migrationTables: List[MigrationTablesSchema]
    version: float
