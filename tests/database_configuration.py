import sys

from utils.configuration import setup_database
from utils.mysql_utils import SQL_connector
from webapp import app

sys.path
sys.path.append("src")

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
print(f"app={app}")
