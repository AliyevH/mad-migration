from datetime import datetime
from src.mysqldb.migration import Migrate as mysql_migrate

###########################
# Get class type of input #
###########################
def get_type(type_name: str) -> object:
    """
    :param type_name: str
    :return: object class
    """
    return {
        'str': str,
        'string': str,

        'int': int,
        'integer': int,

        'float': float,
        'datetime': datetime
    }.get(type_name)


###########################
# Detect db driver fro migration #
###########################
def detect_driver(driver:str) -> object:
    return {
        "mysqldb" : mysql_migrate,
        "psycopg2": mysql_migrate  # heleki ozum verdim ki mende error vermesin

    }.get(driver)