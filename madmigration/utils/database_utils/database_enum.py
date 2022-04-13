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
    

class DatabaseDrivers(Enum):
    pass 
    # MYSQL="mysqldb"
    # "mysql+mysqldb"
    # "pymysql"
    # "mysql+pymysql"
    # "mariadb+pymsql"
    # POSTGRES="psycopg2"
    # "pg8000"
    # "pyodbc"
    # MONGODB="mongodb"
    # # "postgresql+asyncpg"
    # # "asyncpg"