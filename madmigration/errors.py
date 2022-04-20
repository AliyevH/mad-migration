


class TableExists(Exception):
    def __init__(self, message,errors):
      
        self.message = message
        self.errors = errors


class ConfFileDoesNotExists(Exception):
    def __init__(self, message:str = None):
      
        self.message = message if message else 'Configuration file for migration does not exist'


class TableDoesNotExists(Exception):
    def __init__(self, message):
      
        self.message = message


class UnsupportedDatabase(Exception):
    def __init__(self, message):
      
        self.message = message


class CouldNotConnectError(Exception):
    def __init__(self, message=None):

        if message is None:
            message = 'Could not connect to database, check configuration'

        self.message = message


class MissingSourceDBError(Exception):
    def __init__(self, message=None):
        
        if message is None:
            message = 'Missing source database configuration'

        self.message = message
