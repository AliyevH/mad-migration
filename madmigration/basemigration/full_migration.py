from madmigration.db_operations.operations import DBOperations

class FullMigrate():
    def __init__(self, source_db_operations: DBOperations, destination_db_operations: DBOperations):
        self.source_db_operations = source_db_operations
        self.destination_db_operations = destination_db_operations

    def run(self):
        self.create_database_in_destination_if_not_exists()
        self.clone_database()
        self.collect_constraints()
        self.drop_constraints()
        self.copy_data_from_source_to_destination()

    def create_database_in_destination_if_not_exists(self):
        self.destination_db_operations.create_database_if_not_exists()

    def clone_database(self):
        pass

    def collect_constraints(self):
        pass

    def drop_constraints(self):
        pass

    def copy_data_from_source_to_destination(self):
        pass
