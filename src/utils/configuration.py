import os

from dotenv import find_dotenv, load_dotenv

os.environ["GIT_PYTHON_REFRESH"] = "quiet"


def load_env_variables(verbose=0):
    if verbose > 0:
        print(f" -> searching/load for the env files ...")
    list_env_file = [
        env_file
        for env_file in [find_dotenv(".env")] + [find_dotenv(".env-ip")]
        if env_file !=""
    ]
    assert (
        len(list_env_file) > 0
    ), f"\n Neither <.env> nor <.env-ip>  file was found in \
        \n {os.getcwd()}"

    print(f"list_env_file={list_env_file}")

    # loading the env variables
    if verbose > 0:
        print(f" -> loading the env variables")
        print(f"\t- list_env_file={list_env_file}")

    for filepath in list_env_file:
        if verbose > 0:
            print(f"\t- loading: {filepath}")
        load_dotenv(filepath)


def setup_database(database_type="PostgreSQL"):
    # searching/load for the env files
    load_env_variables()
    if database_type == "MySQL":
        # getting the MySQL  credentials
        database_credentials = {
            "username": os.getenv("MYSQL_USER"),
            "password": os.getenv("MYSQL_PASSWORD"),
            "database": os.getenv("MYSQL_DATABASE"),
            "host": os.getenv("MySQL_CNTNR_IP"),
        }
        return database_credentials
    elif database_type == "PostgreSQL":
        database_credentials = {
            "username": os.getenv("POSTGRES_USER"),
            "password": os.getenv("POSTGRES_PASSWORD"),
            "database": os.getenv("POSTGRES_DATABASE"),
            "host": os.getenv("POSTGRES_CNTNR_IP"),
            "port": os.getenv("POSTGRES_HOST_PORT"),
        }
        return database_credentials
    else:
        raise f" datatabse type {database_type} is not define"
