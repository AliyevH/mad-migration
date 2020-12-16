from sqlalchemy.schema import DropConstraint, DropTable
from sqlalchemy.engine import reflection
from madmigration.errors import TableExists
from alembic.migration import MigrationContext
from alembic.operations import Operations
from sqlalchemy import DateTime
from sqlalchemy.dialects.mysql import (
    VARCHAR,
    INTEGER,
    NVARCHAR,
    SMALLINT,
    SET,
    BIGINT,
    BINARY,
    BOOLEAN,
    CHAR,
    DATE,
    DATETIME,
    DECIMAL,
    ENUM,
    FLOAT,
    JSON,
    NUMERIC,
    TEXT,
)
from alembic import op
from collections import defaultdict
from sqlalchemy_utils import UUIDType
from madmigration.config.conf import Config
from madmigration.db_operations.operations import DbOperations
from madmigration.basemigration.base import BaseMigrate
from pprint import pprint


class MysqlMigrate(BaseMigrate): 
    def __init__(self, config: Config,destination_db):
        super().__init__(config,destination_db)
        self.dest_fk = defaultdict(list)
        self.db_operations = MysqlDbOperations(self.engine)
        self.collect_table_names()
        self.collect_drop_fk()
    

    def collect_drop_fk(self):
        """ 
        Collect foreign key constraints for tables so 
        that if something goes wrong, delete everything
        """
        try:
            conn = self.engine.connect()
            transactional = conn.begin()
            inspector = reflection.Inspector.from_engine(self.engine)

            for table_name in inspector.get_table_names():
                if table_name in self.table_list:
                    for fk in inspector.get_foreign_keys(table_name):
                        if not fk["name"]:
                            continue
                        print(fk)
                        print("TT -> ", table_name)
                        self.dest_fk[fk["referred_table"]].append((table_name,fk["name"]))
            transactional.commit()
        except Exception as err:
            print("err -> ",err)
            return False
        finally:
            conn.close()

    def check_table(self, table_name: str) -> bool:
        """ Check table exist or not, and wait user input """
        try:
            if self.engine.dialect.has_table(self.engine.connect(), table_name):
                while True:
                    answ = input(
                        f"Table with name '{table_name}' already exist,\
'{table_name}' table will be dropped and recreated,your table data will be lost,process?(yes/no) "
                    )
                    if answ.lower() == "yes":
                        if self.dest_fk[table_name]:
                            self.db_operations.drop_fk(self.dest_fk[table_name])
                        self.db_operations.drop_table(table_name)
                        return False
                    elif answ.lower() == "n":
                        return True
                    else:
                        continue
            return False
        except Exception as err:
            print(err)
            return False

    @staticmethod
    def get_column_type(type_name: str) -> object:
        """Get class of db type
        :param type_name: str
        :return: object class
        """
        return {
            "string": VARCHAR,
            "varchar": VARCHAR,
            "integer": INTEGER,
            "nvarchar": NVARCHAR,
            "smallint": SMALLINT,
            "set": SET,
            "bigint": BIGINT,
            "binary": BINARY,
            "boolean": BOOLEAN,
            "bool": BOOLEAN,
            "char": CHAR,
            "date": DATE,
            "datetime": DATETIME,
            "decimal": DECIMAL,
            "enum": ENUM,
            "float": FLOAT,
            "json": JSON,
            "numeric": NUMERIC,
            "text": TEXT,
            "uuid": UUIDType(binary=False),
        }.get(type_name.lower())


class MysqlDbOperations(DbOperations):
    def drop_fk(self,fk_constraints: str):
        try:
            conn = self.engine.connect()
            ctx = MigrationContext.configure(conn)
            op = Operations(ctx)
            # [('todo', 'todo_ibfk_1')]
            for fk in fk_constraints:
                op.drop_constraint(fk[1], fk[0], type_="foreignkey", schema=None)
        except Exception as err:
            print("fk_drop -> ",err)
        finally:
            conn.close()