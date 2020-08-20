from pydantic import BaseModel
from typing import Union, List, Any, AnyStr, Dict


class ForeignKeySchema(BaseModel):
    use_alter: bool = True
    table_name: str
    column_name: str
    ondelete: str = "CASCADE"

class OptionsSchema(BaseModel):
    primary_key: bool = False
    nullable: bool = False
    default: bool = None
    index: bool = None
    unique: bool = None
    autoincrement: bool = True
    foreign_key: ForeignKeySchema = None
    length: int = None
    type: str

    type_cast: AnyStr = None


class SourceConfigSchema(BaseModel):
    SourceConfig: Dict[str, str]


class DestinationConfigSchema(BaseModel):
    DestinationConfig: Dict[str, str]


class SourceTableSchema(BaseModel):
    name: Dict[str, str]

class DestinationColumn(BaseModel):
    name: str
    options: OptionsSchema


class ColumnParametersSchema(BaseModel):
    destinationColumn: DestinationColumn
    sourceColumn: Any


class TablesInfo(BaseModel):
    SourceTable: Dict[str, str]
    DestinationTable: Dict[str, str]
    MigrationColumns: List[ColumnParametersSchema]


class MigrationTablesSchema(BaseModel):
    migrationTable: TablesInfo


class ConfigSchema(BaseModel):
    Configs: List[Union[SourceConfigSchema, DestinationConfigSchema]]
    migrationTables: List[MigrationTablesSchema]
    version: float
