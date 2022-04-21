from abc import ABC, abstractmethod


class DatabaseBaseConnection(ABC):
    @property
    @abstractmethod
    def driver(self):
        raise NotImplementedError()

    @property
    @abstractmethod
    def db_name(self):
        raise NotImplementedError()

    @abstractmethod
    def _check_database_exist(self):
        raise NotImplementedError()

    @abstractmethod
    def _create_database(self):
        raise NotImplementedError()

    @abstractmethod
    def _create_connection(self):
        raise NotImplementedError()

    @abstractmethod
    def all_db_tables(self):
        raise NotImplementedError()

    @abstractmethod
    def close(self):
        raise NotImplementedError()

