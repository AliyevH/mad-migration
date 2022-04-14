from dataclasses import dataclass
from typing import Optional


@dataclass
class DatabaseDetails:
    database: str
    dialect_name: str
    dialect_driver: Optional[str] = None