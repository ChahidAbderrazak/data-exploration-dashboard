import csv
from io import StringIO
from typing import List

from fastapi import FastAPI, File, HTTPException, UploadFile
from mysql.connector import Error
from pydantic import BaseModel

from src.lib.configuration import setup_database
from src.lib.mysql_utils import MySQL_connector

app = FastAPI()

# Database connection parameters
database_credentials = setup_database()
table_name = "product"
root_folder = "data/Tables"
upload_folder = "data/tmp"
# Define where to save uploaded files

# Create the directory if it doesn't exist
import shutil
from pathlib import Path

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


MySQL = MySQL_connector(
    root_folder=root_folder,
    username=database_credentials["username"],
    password=database_credentials["password"],
    database=database_credentials["database"],
    host=database_credentials["host"],
)

def send_query(query):
    try:
        conn = MySQL.mydb
        cursor = conn.cursor()
        cursor.execute(query)
        conn.commit()
        cursor.close()
        conn.close()
    except Exception as e:
        print(f"warning: {e}")

def create_table(table_name="table"):
    try:
        query = f"CREATE TABLE {table_name} ( \
                            id INT AUTO_INCREMENT PRIMARY KEY, \
                            name VARCHAR(100),\
                            description TEXT,\
                            price DECIMAL(10, 2)\
                            );"

        #  send the query
        send_query(query)

        return 0
    except:
        return 1


def delete_table(table_name="table"):
    query = f"DROP TABLE {table_name};"

    #  send the query
    send_query(query)


# initialization
def does_table_Exists(table_name="table"):
    conn = MySQL.mydb
    cursor = conn.cursor()
    cursor.execute("SHOW tables;")
    list_tables = cursor.fetchall()
    for table_ in list_tables:
        print("table name", table_[0])
        if table_[0] == table_name:
            return True
    return False


if not does_table_Exists(table_name):
    create_table(table_name)


# Create item
@app.post("/items/", response_model=ItemResponse)
def create_item(item: Item):
    """
    insert a new row to the product table
    """
    try:
        conn = MySQL.mydb
        cursor = conn.cursor()
        query = f"INSERT INTO {table_name} (name, description, price) VALUES (%s, %s, %s)"
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
        conn = MySQL.mydb
        cursor = conn.cursor(dictionary=True)
        query = f"SELECT * FROM {table_name}"
        cursor.execute(query)
        items = cursor.fetchall()
        cursor.close()
        conn.close()
        return items
    except Error as e:
        raise HTTPException(status_code=500, detail="Database error")


# Get item by ID
@app.get("/items/{item_id}", response_model=ItemResponse)
def get_item(item_id: int):
    """
    Retrieve the row of the id={item_id} from the product table
    """
    try:
        conn = MySQL.mydb
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
        raise HTTPException(status_code=500, detail="Database error")


# Update item
@app.put("/items/{item_id}", response_model=ItemResponse)
def update_item(item_id: int, item: Item):
    """
    Update the row of the id={item_id} from the product table
    """
    try:
        conn = MySQL.mydb
        cursor = conn.cursor()
        query = (
            f"UPDATE {table_name} SET name = %s, description = %s, price = %s WHERE id = %s"
        )
        cursor.execute(query, (item.name, item.description, item.price, item_id))
        conn.commit()
        cursor.close()
        conn.close()
        if cursor.rowcount == 0:
            raise HTTPException(status_code=404, detail="Item not found")
        return {**item.dict(), "id": item_id}
    except Error as e:
        raise HTTPException(status_code=500, detail="Database error")


# Delete item
@app.delete("/items/{item_id}")
def delete_item(item_id: int):
    """
    Delete the row of the id={item_id} from the product table
    """
    try:
        conn = MySQL.mydb
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
        raise HTTPException(status_code=500, detail="Database error")


def is_empty_row(row):
    return all(field == "" for field in row)


@app.post("/upload-csv/")
async def upload_csv(file: UploadFile = File(...)):
    """
    Upload data from a CSV file
    """
    # Check if the uploaded file is a CSV file
    if file.content_type != "text/csv":
        raise HTTPException(
            status_code=400, detail="Invalid file type. Please upload a CSV file."
        )
    # Save the uploaded image
    csv_path = f"{upload_folder}/{file.filename}"
    with open(csv_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    try:
        # Read the file content as a string
        content = await file.read()

        # Decode the content to string
        decoded_content = content.decode("utf-8")

        # Use StringIO to treat the string as a file-like object for CSV reader
        csv_reader = csv.reader(StringIO(decoded_content))

        # Process CSV data
        csv_data = []
        for idx, row in enumerate(csv_reader):
            if not is_empty_row(row):
                csv_data.append(row)  # Do whatever processing you need here
                print(f"row{idx}= {row}")

        return {"filename": file.filename, "data": csv_data}

    except Exception as e:
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

        return {"filename": file.filename, "message": "Image uploaded successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error saving file: {str(e)}")

