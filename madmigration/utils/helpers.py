import os
import sys
from pathlib import Path
from datetime import datetime, date
from enum import Enum
from uuid import uuid4, UUID


from sqlalchemy.schema import DropTable
from sqlalchemy.schema import ForeignKeyConstraint
from sqlalchemy.ext.compiler import compiles
from sqlalchemy.engine.url import make_url

from madmigration.utils.logger import configure_logging

logger = configure_logging(__name__)

@compiles(DropTable, "postgresql")
def _compile_drop_table(element, compiler, **kwargs):
    """
    Drop table cascade with foreignkeys
    https://stackoverflow.com/questions/38678336/sqlalchemy-how-to-implement-drop-table-cascade# 
    """
    return compiler.visit_drop_table(element) + " CASCADE"


@compiles(ForeignKeyConstraint, "mysql", "mariadb")
def process(element, compiler, **kw):
    element.deferrable = element.initially = None
    return compiler.visit_foreign_key_constraint(element, **kw)


def check_file(file):
    return Path(file).is_file() and os.access(file, os.R_OK)


def file_not_found(file):
    logger.error(f"Given file does not exists file: {file}")
    sys.exit(1)


def issue_url():
    return "https://github.com/MadeByMads/mad-migration/issues"


def app_name():
    return "madmigrate"


def parse_uri(uri):
    return make_url(uri).database


def database_not_exists(database):
    """This function will be executed if there is no database exists """

    database = parse_uri(database)

    usage = [
        "",
        f"😭 Error: Source database '{database}'  does not exists",
        "",
        f"Run '{app_name()} --help' for usage.",
        "",
        f"🥳  if you think something is wrong please feel free to open issues 👉'{issue_url()}'👈 ",
        "",
        "Exiting ...",
        "",
    ]
    return "\n".join(usage)


def goodby_message(message, exit_code=0):
    print(message, flush=True)
    logger.error(message)
    sys.exit(int(exit_code))


def get_type_object(data_type):
        return {
            "UUID": UUID,
            "uuid": uuid4,
            
            "string": str,
            "str": str,
            "varchar": str,
            "text": str,
            "nvarchar": str,
            "smallint": int,
            "char": str,

            "int": int,
            "integer": int,
            "bigint": int,

            "float": float,
            "numeric": float,
            "decimal": float,

            "date": date,
            "datetime": datetime,

            "binary": bytes,
            "enum": Enum,
            "set": set,

            "json": dict,

            "boolean": bool,
            "bool": bool,

        }.get(data_type.lower())