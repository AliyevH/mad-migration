


class TableExists(Exception):
    def __init__(self, message,errors):
      
        self.message = message
        self.errors = errors


class ConfFileDoesNotExists(Exception):
    def __init__(self, message):
      
        self.message = message


class TableDoesNotExists(Exception):
    def __init__(self, message):
      
        self.message = message


class UnsupportedDatabase(Exception):
    def __init__(self, message):
      
        self.message = message
