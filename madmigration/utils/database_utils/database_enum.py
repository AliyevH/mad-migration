from enum import Enum

class DatabaseTypes(Enum):
    POSTGRES='postgresql'
    MYSQL='mysql'
    MSSQL='mssql'
    SQLITE='sqlite'
    ORACLE='oracle'
    MONGODB='mongodb'


class DBHandler(Enum):
    SQL='sql'
    MONGO='mongo'
    