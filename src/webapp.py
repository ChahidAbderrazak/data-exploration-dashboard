import io
import os
import shutil
from pathlib import Path
from typing import List
import pandas as pd
import uvicorn
from fastapi import FastAPI, File, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from mysql.connector import Error
from pydantic import BaseModel

from utils.configuration import setup_database
from utils.data_exploration import *
from utils.mysql_utils import SQL_connector

app = FastAPI()

origins = ["http://localhost:4200", "http://0.0.0.0:4200", "http://127.0.0.1:4200"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Database connection parameters
database_type = "MySQL"  # "PostgreSQL"
database_credentials = setup_database(database_type=database_type)
print(f"database_credentials={database_credentials}")
table_name = "product"
root_folder = "data/Tables"
upload_folder = "data/tmp"
create_table_query = f"""
            CREATE TABLE {table_name} (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    name VARCHAR(100),
                    description TEXT,
                    price DECIMAL(10, 2)
                    );
            """

# Define where to save uploaded files
## Create the directory if it doesn't exist
Path(root_folder).mkdir(parents=True, exist_ok=True)
Path(upload_folder).mkdir(parents=True, exist_ok=True)


# Pydantic models for request and response validation
class Item(BaseModel):
    name: str
    description: str
    price: float


class ItemResponse(BaseModel):
    id: int
    name: str
    description: str
    price: float

    class Config:
        orm_mode = True


demo_item = Item(name="banana", description="description", price="10")

MySQL = SQL_connector(
    database_type=database_type,
    root_folder=root_folder,
    username=database_credentials["username"],
    password=database_credentials["password"],
    database=database_credentials["database"],
    host=database_credentials["host"],
)
# create a table if it does not exist
MySQL.create_table(table_name=table_name, query=create_table_query)


# Create item
@app.post("/items/", response_model=ItemResponse)
def create_item(item: Item):
    """
    insert a new row to the product table
    """
    try:
        conn = MySQL.connection
        cursor = conn.cursor()
        query = (
            f"INSERT INTO {table_name} (name, description, price) VALUES (%s, %s, %s)"
        )
        cursor.execute(query, (item.name, item.description, item.price))
        conn.commit()
        item_id = cursor.lastrowid
        cursor.close()
        conn.close()
        return {**item.dict(), "id": item_id}
    except Error as e:
        print(f" error: {e}")
        raise HTTPException(status_code=500, detail="Database error")


# Get all items
@app.get("/items/", response_model=List[ItemResponse])
def get_items():
    """
    Retrieve all row from the product table
    """
    try:
        conn = MySQL.connection
        cursor = conn.cursor(dictionary=True)
        query = f"SELECT * FROM {table_name}"
        cursor.execute(query)
        items = cursor.fetchall()
        cursor.close()
        conn.close()
        return items
    except Error as e:
        print(f"error: {e}")
        raise HTTPException(status_code=500, detail="Database error")


# Get item by ID
@app.get("/items/{item_id}", response_model=ItemResponse)
def get_item(item_id: int):
    """
    Retrieve the row of the id={item_id} from the product table
    """
    try:
        conn = MySQL.connection
        cursor = conn.cursor(dictionary=True)
        query = f"SELECT * FROM {table_name} WHERE id = %s"
        cursor.execute(query, (item_id,))
        item = cursor.fetchone()
        cursor.close()
        conn.close()
        if item is None:
            raise HTTPException(status_code=404, detail="Item not found")
        return item
    except Error as e:
        print(f"error: {e}")
        raise HTTPException(status_code=500, detail="Database error")


# Update item
@app.put("/items/{item_id}", response_model=ItemResponse)
def update_item(item_id: int, item: Item):
    """
    Update the row of the id={item_id} from the product table
    """
    try:
        conn = MySQL.connection
        cursor = conn.cursor()
        query = f"UPDATE {table_name} SET name = %s, description = %s, price = %s WHERE id = %s"
        cursor.execute(query, (item.name, item.description, item.price, item_id))
        conn.commit()
        cursor.close()
        conn.close()
        if cursor.rowcount == 0:
            raise HTTPException(status_code=404, detail="Item not found")
        return {**item.dict(), "id": item_id}
    except Error as e:
        print(f"error: {e}")
        raise HTTPException(status_code=500, detail="Database error")


# Delete item
@app.delete("/items/{item_id}")
def delete_item(item_id: int):
    """
    Delete the row of the id={item_id} from the product table
    """
    try:
        conn = MySQL.connection
        cursor = conn.cursor()
        query = f"DELETE FROM {table_name} WHERE id = %s"
        cursor.execute(query, (item_id,))
        conn.commit()
        cursor.close()
        conn.close()
        if cursor.rowcount == 0:
            raise HTTPException(status_code=404, detail="Item not found")
        return {"detail": "Item deleted"}
    except Error as e:
        print(f"error: {e}")
        raise HTTPException(status_code=500, detail="Database error")


def is_empty_row(row):
    return all(field == "" for field in row)


@app.post("/upload-csv/")
async def upload_csv(file: UploadFile = File(...)):
    """
    Upload data from a CSV file
    """
    # Check if the uploaded file is a CSV file
    filename, file_extension = os.path.splitext(file.filename)
    print(f"file_extension={file_extension}")
    if (
        file.content_type != "text/csv"
        and file_extension != ".xltx"
        and file_extension != ".xlsx"
    ):
        raise HTTPException(
            status_code=400,
            detail="Invalid file type. Please upload a CSV/xltx/xlsx file.",
        )

    try:
        # Read the file content as a string
        content = await file.read()
        nrows = 10  # None

        # Use StringIO to treat the string as a file-like object for CSV reader
        if file_extension == ".xltx" or file_extension == ".xlsx":
            filename_path = io.BytesIO(content)
            df = pd.read_excel(io.BytesIO(content), nrows=nrows)
        elif file_extension == ".csv":
            filename_path = io.BytesIO(content)
            df = pd.read_csv(io.BytesIO(content), nrows=nrows)
        else:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid file extension ({file_extension}). Please upload CSV/xltx/xlsx file types.",
            )

        stats_dict={}
        print(f"\n\n - Data analysis in process ...")


        # ###-------------------------------------------------------------
        # # initialize the spark sessions
        # spark = init_spark(MAX_MEMORY="4G")

        # # Load the main data set into pyspark data frame
        # spark_df = spark_load_data(spark, filename_path)

        # ###-------------------------------------------------------------
        # # run the  data preparation pipeline
        # spark_df, missing_invalid_df = data_preparation_pipeline(spark, spark_df)

        # # run the data analysis pipeline
        # monthly_sales, past_sales_stats_df,current_sales_stats_df,growth_rate_dict,\
        # top_ranked_clients_df,worst_ranked_clients_df,\
        #     top_purchases_by_gender_df = data_analysis_pipeline(spark, spark_df, topN=5, verbose=0)

        # ###-------------------------------------------------------------
        # df = pd.DataFrame()  # df.to_dict(orient="list")
        # df["DateByMonth"] = monthly_sales["DateByPeriod"]
        # df["IncomeByMonth"] = monthly_sales["sum_Purch_Amt"]
        # # df["Price"] = monthly_sales["avg_Price"]
        # # df["Age"] = monthly_sales["avg_Age"]
        # # df["Returns"] = monthly_sales["sum_Returns"]
        # # df["Churn"] = monthly_sales["sum_Churn"]

        # data_dict = df.to_dict(orient="records")  # orient="list")

        # # growth


        # # growth_rate_dict
        # # stats_dict.update({"growth_rate": growth_rate_dict})

        # # past_sales_dict = past_sales_stats_df.round(1).to_dict(orient="records")
        # # stats_dict.update({"past_sales": past_sales_dict})

        # # current_sales_dict = current_sales_stats_df.round(1).to_dict(orient="records")
        # # stats_dict.update({"current_sales": current_sales_dict})

        # # top_clients_dict=top_ranked_clients_df.astype(str).to_dict(orient="records")
        # # stats_dict.update({"top_clients": top_clients_dict})

        # # # Clients
        # # clients = pd.DataFrame()  # df.to_dict(orient="list")
        # # clients["DateByMonth"] = top_ranked_clients_df["DateByPeriod"]

        # get the other data
        data_dict = df.to_dict(orient="records")  # orient="list")
        print(f"csv_data={data_dict}")
        metadata = {
            "topic": "raw data",
            "filename": file.filename,
            "num_rows": df.shape[0],
            "num_columns": df.shape[1],
            "columns": df.columns.tolist(),
        }

        return {
            "status": "success",
            "metadata": metadata,
            "data": data_dict,
            "stats": stats_dict,
        }

    except Exception as e:
        print(f"error: {e}")
        raise HTTPException(status_code=500, detail=f"Error processing file: {str(e)}")


@app.post("/upload-image/")
async def upload_image(file: UploadFile = File(...)):
    """
    Upload and image file
    """

    # Check if the uploaded file is an image
    if file.content_type not in ["image/jpeg", "image/png", "image/gif"]:
        raise HTTPException(
            status_code=400,
            detail="Invalid file type. Please upload an image (jpeg, png, gif).",
        )

    try:
        # Save the uploaded image
        image_path = f"{upload_folder}/{file.filename}"
        with open(image_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        return {
            "status": "success",
            "filename": file.filename,
            "message": "Image uploaded successfully",
        }
    except Exception as e:
        print(f"error: {e}")
        raise HTTPException(status_code=500, detail=f"Error saving file: {str(e)}")


def prepare_parser():
    from argparse import ArgumentParser

    parser = ArgumentParser(description="Code template")
    parser.add_argument(
        "--port",
        default=8080,
        metavar="input port",
        help="API server port",
        type=str,
    )
    parser.add_argument(
        "--host",
        default="0.0.0.0",
        metavar="host IP address",
        help="API server IP address",
        type=str,
    )

    return parser


if __name__ == "__main__":
    # get the input parameters
    parser = prepare_parser()
    args = parser.parse_args()

    # run the UVICORN server
    uvicorn.run(app, host=args.host, port=args.port)
