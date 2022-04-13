from dataclasses import dataclass


@dataclass
class DatabaseDetails:
    database: str
    dialect_name: str
    dialect_driver: str