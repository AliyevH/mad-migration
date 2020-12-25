


class TableExists(Exception):
    def __init__(self, message,errors):
      
        self.message = message
        self.errors = errors


class FileDoesNotExists(Exception):
    def __init__(self, message):
      
        self.message = message


class TableDoesNotExists(Exception):
    def __init__(self, message):
      
        self.message = message
