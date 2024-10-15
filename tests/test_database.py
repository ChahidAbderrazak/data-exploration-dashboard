###------------------------------------------------------------------------------------------------
import os

import pytest

# check if we are on GITHUB_ACTIONS
IN_GITHUB_ACTIONS = os.getenv("GITHUB_ACTIONS") == "true"
# Skip pytest if we are on GITHUB_ACTIONS
if True:#IN_GITHUB_ACTIONS:
    def test_IN_GITHUB():
        pass
    pytest.skip(reason="Test doesn't work in Github Actions.", allow_module_level=True)
###------------------------------------------------------------------------------------------------

from lib.configuration import setup_database
from lib.mysql_utils import SQL_connector


root_folder = "data/TestTables"
database_type_list = ("PostgreSQL", "MySQL", "WrongSQL")
database_type = database_type_list[1]
database_credentials = setup_database(database_type=database_type)
print(f"\n\n - database_credentials={database_credentials}")
table_name = "test"


# connect to the database
MySQL = SQL_connector(
    database_type=database_type,
    root_folder=root_folder,
    username=database_credentials["username"],
    password=database_credentials["password"],
    database=database_credentials["database"],
    host=database_credentials["host"],
)

class Test_SQL_connector:
    def test_create_database(self):

        # test connectivity
        try:
            # the error will occur if the cursor is not defines
            self.connection = MySQL.connection
            self.cursor = self.connection.cursor()
        except Exception as e:
            raise e

    def test_create_table(self):
        # create table
        create_table_query = f"""
                CREATE TABLE {table_name} (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    name VARCHAR(100) UNIQUE,  -- UNIQUE constraint to demonstrate error handling
                    description TEXT
                );
                """
        MySQL.create_table(table_name=table_name, query=create_table_query)

    def test_delete_table(self):
        # delete table
        MySQL.delete_table(table_name=table_name)
