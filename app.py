from db_init.connection_engine import SourceDB
from db_init.connection_engine import DestinationDB
from config.conf import config

# Source and Destination DB Initialization with session
sourceDB = SourceDB()
destinationDB = DestinationDB()


def run():
    if "mysql" in destinationDB.engine.driver:
        from src.mysqldb.migration import Migrate
        Migrate()



# ###########################
# # Migration Function from one table column into another one #
# ###########################
# def column_to_column():
#
#     # View rows and updated rows at the end of function
#     ROWS = 0
#     INSERTED_ROWS = 0
#
#     # Loop in migration tables from yaml list 'migrationTables'
#     for mt in config.migrationTables:
#         for k, v in mt.items():
#
#             # Get source table name 'SourceTableName'
#             # Get destination table name 'DestinationTableName'
#             source_table_name = v.get("SourceTableName")
#             destination_table_name = v.get("DestinationTableName")
#             unique_key = v.get("uniqueKey")
#
#             # Get migration columns
#             migration_columns = v.get("MigrationColumns")
#
#             # Get source and destination table object from base.classes automap
#             source_table = getattr(sourceDB.base.classes, source_table_name)
#             destination_table = getattr(destinationDB.base.classes, destination_table_name)
#
#             print(dir(source_table))
#             print(source_table.capacity.property.__dir__())
#             print(source_table.capacity.property.columns)
#
#     #         # Get all rows from sourceDB session
#     #         source_rows = sourceDB.session.query(source_table).all()
#     #
#     #         for row in source_rows:
#     #             ROWS += 1
#     #             data = {}
#     #
#     #             for mc in migration_columns:
#     #
#     #                 # If type_cast specified convert data into specified type
#     #                 if mc.get("type_cast"):
#     #                     if 'datetime' in mc.get("type_cast"):
#     #                         destination_datetime, *format = mc.get("type_cast").split("=")
#     #                         column_class_type = get_type(destination_datetime)
#     #
#     #                     # Get type of class that the data will be converted [int, str, float]
#     #                     else:
#     #                         column_class_type = get_type(mc.get("type_cast"))
#     #
#     #                     temp = getattr(row, mc.get("sourceColumn"))
#     #
#     #                     # Try to convert data into specified type (type_cast)
#     #                     try:
#     #                         if format:
#     #                             print(column_class_type(temp, format[0]))
#     #                             setattr(row, mc.get("sourceColumn"), column_class_type(temp, format[0]))
#     #                             print(row)
#     #
#     #                         setattr(row, mc.get("sourceColumn"), column_class_type(temp))
#     #
#     #                     # If get exception set None
#     #                     except Exception as err:
#     #                         setattr(row, mc.get("sourceColumn"), None)
#     #
#     #                 # Update data dictionary
#     #                 data.update({mc.get("destinationColumn"): getattr(row, mc.get("sourceColumn"))})
#     #
#     #             # Try to insert into new table
#     #             # try:
#     #             #     inserting_data = destination_table(**data)
#     #             #     destinationDB.session.add(inserting_data)
#     #             #     destinationDB.session.commit()
#     #             #     INSERTED_ROWS += 1
#     #             # # If Exception rollback transaction
#     #             # except Exception as err:
#     #             #     destinationDB.session.rollback()
#     #             #     print(err)
#     #             #     print(data)
#     #             #     sleep(60)
#     #
#     # # At the end close database sessions
#     # sourceDB.session.close()
#     # destinationDB.session.close()
#     #
#     # # View how many rows exists and how many rows inserted
#     # print(ROWS, INSERTED_ROWS)
#
#
# column_to_column()



