from enum import Enum

class DatabaseTypes(Enum):
    POSTGRES='postgresql'
    MYSQL='mysql'
    MSSQL='mssql'
    SQLITE='sqlite'
    MONGODB='mongodb'


class DBHandler(Enum):
    SQL='sql'
    MONGO='mongo'
    