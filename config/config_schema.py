from pydantic import BaseModel
from typing import Union,List,Any,AnyStr,Dict,Mapping
from datetime import datetime

class OptionsSchema(BaseModel):
    fkey: bool = False
    unique: bool = False
    nullable: bool = False
    type_cast: AnyStr = None

class SourceConfigSchema(BaseModel):
    SourceConfig: Dict[str,str]

class DestinationConfigSchema(BaseModel):
    DestinationConfig: Dict[str,str]


class ColumnParameters(BaseModel):
    destinationColumn: Any
    sourceColumn: Any
    options: OptionsSchema = None

class TablesInfo(BaseModel):
    SourceTableName: Any = None
    DestinationTableName : Any = None
    MigrationColumns: List[ColumnParameters]

class MigrationTablesSchema(BaseModel):
    migrationTable: TablesInfo

class ConfigSchema(BaseModel):
    Configs: List[Union[SourceConfigSchema,DestinationConfigSchema]]
    migrationTables: List[MigrationTablesSchema]