import time
import warnings
# for MySQL
import mysql.connector

# for PostgresSQL
import psycopg2
from mysql.connector import errorcode
from psycopg2 import errorcodes


class MySQL_connector:
    def __init__(
        self,
        root_folder,
        username,
        password,
        database,
        host="localhost",
        port="",
        create_table_query="",
    ):
        self.root_folder = root_folder
        self.username = username
        self.password = password
        self.database = database
        self.host = host
        self.port = port

        # create the table
        #  display
        self.database_info()

        # initialise the database
        self.connect_to_database()

    def database_info(self):
        print(f"---------------------------------")
        print(f"-      connecting to MySQL ")
        print(f"- database={self.database}")
        print(f"- username={self.username}")
        print(f"- host={self.host}")
        print(f"- port={self.port}")
        print(f"---------------------------------")

    def connect_SQL(self):
        try:
            # conenct to the database
            self.connection = mysql.connector.connect(
                host=self.host,
                user=self.username,
                password=self.password,
                database=self.database,
            )

            if self.connection.is_connected():
                print("Connected to MySQL database successfully !!")
            self.cursor = self.connection.cursor()

            return False

        # The SQL connection has errors
        except mysql.connector.Error as err:
            # Print the error message
            print(f"Error: {err}")
            # Handle specific error codes
            if err.errno == 1062:
                print(
                    f"Error: Duplicate entry for unique key (Duplicate entry). Error Code: {err.errno}"
                )
            elif err.errno == 1049:
                print(f"Error: Unknown database. Error Code: {err.errno}")
            elif err.errno == errorcode.ER_BAD_DB_ERROR:
                print(
                    f"Error: Table [{self.database}] doesn't exist. Error Code: {err.errno}"
                )
            elif err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
                print(
                    f"Error: Access denied for user [{self.username}]. Error Code: {err.errno}"
                )
            # else:
            #     print(f"General MySQL Error. Error Code: {err.errno}")

            return True

    def connect_to_database(self, max_attempt=3, delay=2):
        print(f"---------------------------------------")
        print(f"-  connecting to MySQL database: {self.host}/{self.database}")
        print(f"---------------------------------------")
        attempt = 0
        while attempt < max_attempt:
            # increase attempt
            attempt += 1

            # setting up the database connection
            err = self.connect_SQL()
            if not err:
                break

            # progressive reconnect delay
            time.sleep(delay**attempt)
            attempt += 1


class PostgreSQL_connector:
    def __init__(
        self,
        root_folder,
        username,
        password,
        database,
        host="localhost",
        port="",
        create_table_query="",
    ):
        self.root_folder = root_folder
        self.username = username
        self.password = password
        self.database = database
        self.host = host
        self.port = port

        #  display
        self.database_info()

        # initialise the database
        self.connect_to_database()

    def database_info(self):
        print(f"---------------------------------")
        print(f"-      connecting to PostgreSQL ")
        print(f"- database={self.database}")
        print(f"- username={self.username}")
        print(f"- host={self.host}")
        print(f"- port={self.port}")
        print(f"---------------------------------")

    def connect_SQL(self):
        try:
            # conenct to the database
            self.connection = psycopg2.connect(
                dbname=self.database,
                user=self.username,
                password=self.password,
                host=self.host,
                port=self.port,
            )

            if self.connection.is_connected():
                print("Connected to PostgreSQL database successfully !!")
            self.cursor = self.connection.cursor()

            return False

        # The SQL connection has errors
        except psycopg2.Error as error:
            # Print the error message
            print(f"Database operation failed: {error}")

            # Handle specific error codes
            if error.pgcode == errorcodes.UNIQUE_VIOLATION:
                print(
                    f"Error: Duplicate value found (Unique constraint violation). Error Code: {error.pgcode}"
                )
            elif error.pgcode == errorcodes.SYNTAX_ERROR:
                print(
                    f"Error: Syntax error in the SQL query. Error Code: {error.pgcode}"
                )
            elif error.pgcode == errorcodes.FOREIGN_KEY_VIOLATION:
                print(f"Error: Foreign key violation. Error Code: {error.pgcode}")
            else:
                print(f"General Database Error. Error Code: {error.pgcode}")
            return True

    def connect_to_database(self, max_attempt=3, delay=2):
        print(f"---------------------------------------")
        print(f"-  connecting to PostgreSQL database: {self.host}/{self.database}")
        print(f"---------------------------------------")
        attempt = 0
        while attempt < max_attempt:
            # increase attempt
            attempt += 1

            # setting up the database connection
            err = self.connect_SQL()
            if not err:
                break

            # progressive reconnect delay
            time.sleep(delay**attempt)
            attempt += 1


class SQL_connector:
    def __init__(
        self,
        database_type,
        root_folder,
        username,
        password,
        database,
        host="127.0.0.1",
        port="",
    ):
        self.database_type = database_type
        self.root_folder = root_folder
        self.username = username
        self.password = password
        self.database = database
        self.host = host
        self.port = port
        #  display
        self.database_info()

        # setting up the database connection
        if database_type == "PostgreSQL":
            self.Database = PostgreSQL_connector(
                root_folder=self.root_folder,
                username=self.username,
                password=self.password,
                database=self.database,
                host=self.host,
                port=self.port,
            )

        elif database_type == "MySQL":
            self.Database = MySQL_connector(
                root_folder=root_folder,
                username=username,
                password=password,
                database=database,
                host=host,
                port=port,
            )

        else:
            self.Database = None
            raise f" datatabse type {database_type} is not define"

        # set conenct cursor
        self.connection = self.Database.connection
        self.cursor = self.connection.cursor()

    def database_info(self):
        print(f"---------------------------------")
        print(f"-  DATABASE SELECTOR : ")
        print(f"- database_type={self.database_type}")
        print(f"- root_folder={self.root_folder}")
        print(f"---------------------------------")

    def does_table_Exists(self, table_name="table"):

        self.cursor.execute("SHOW tables;")
        list_tables = self.cursor.fetchall()
        for table_ in list_tables:
            print("table name", table_[0])
            if table_[0] == table_name:
                return True
        return False

    def send_query(self, query):
        # Example: Create a table with a UNIQUE constraint
        try:
            self.cursor.execute(query)
            self.connection.commit()

        except Exception as e:
            print(f"Query error: {e}")

        return self.cursor

    def create_table(self, table_name, query):
        # delete the table if it exists
        if self.does_table_Exists(table_name):
            # self.delete_table(table_name)
            print("Table already exists!")
        else:
            # apply the create table query
            self.send_query(query)
            assert self.does_table_Exists(table_name=table_name)
            print("Table created successfully!")

    def delete_table(self, table_name):
        delete_table_query = f"DROP TABLE {table_name};"

        if self.does_table_Exists(table_name=table_name):
            # apply the query
            self.send_query(delete_table_query)
            assert not self.does_table_Exists(table_name=table_name)
            print("Table deleted successfully!")

    def search_for_sample(self, table_name, data={}):
        """Check that the item was actually inserted into the database"""

        # build the search query
        query = f"SELECT * from {table_name} "
        if len(data) > 0:
            query += " where "
            for idx, key in enumerate(data.keys()):
                query += f""" {key}="{data[key]}" """
                if idx < len(data) - 1:
                    query += " AND "

        # run the query
        cursor = self.connection.cursor(dictionary=True)
        cursor.execute(query)
        items = cursor.fetchall()
        cursor.close()

        if len(data) > 0 and len(items)>1:
            warnings.warn(
                f"\n\nWarning: the record {data} seems to have {len(items)} duplicate : \n{items}"
            )
        return items


if __name__ == "__main__":

    root_folder = "data/Tables"
    username = "user"
    password = "password"
    database = "database"
    host = "127.0.0.1"

    sql_cnx = SQL_connector(
        root_folder=root_folder,
        username=username,
        password=password,
        database=database,
        host=host,
    )
