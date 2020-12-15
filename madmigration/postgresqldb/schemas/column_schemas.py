from pydantic import BaseModel
from typing import Union,Any


class FloatSchema(BaseModel):
    precision: Union[int,None] = None

class RealSchema(FloatSchema):
    pass

class NumericSchema(FloatSchema):
    scale: Union[int,None] = None

class VarcharSchema(BaseModel):
    length: int = 256

class ArraySchema(BaseModel):
    dimensions: Union[int,None] = None
    itemtype: Any

class CharSchema(VarcharSchema):
    pass

class TimeStampSchema(BaseModel):
    timezone: bool = False 

class TimeSchema(TimeStampSchema):
    pass