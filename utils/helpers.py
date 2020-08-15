from datetime import datetime


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
