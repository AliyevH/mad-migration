


# __all__ = (
#     "TableExists"

# )


class TableExists(Exception):
    def __init__(self, message,errors):
      
        self.message = message
        self.errors = errors
