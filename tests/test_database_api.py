# --------------------------------------------------------------------------------------------------
import os
import sys
import numpy as np
import pytest

sys.path
sys.path.append("src")
from fastapi.testclient import TestClient
from testing_configuration import *

from webapp import MySQL, app, create_table_query, table_name

# check if we are on GITHUB_ACTIONS
IN_GITHUB_ACTIONS = os.getenv("GITHUB_ACTIONS") == "true"
# Skip pytest if we are on GITHUB_ACTIONS
if IN_GITHUB_ACTIONS:
    pytest.skip(reason="Test doesn't work in Github Actions.", allow_module_level=True)
# --------------------------------------------------------------------------------------------------

# Instantiate the client
client = TestClient(app)
print(f" root={os.getcwd()}")


@pytest.mark.skip(reason="already validated")
# @pytest.mark.skipif(sys.version_info < (3, 8), reason="Requires Python 3.8 or later.")
class Test_Dashboard_APIs:

    def test_server_running(self):
        response = client.get("/server")
        assert response.status_code == 200
        assert response.json() == {"status": "success"}

    def test_upload_image(self):
        # Define the path to the test image
        image_path = "data/test/image.jpg"

        # Make sure the file exists before running the test
        assert os.path.exists(image_path), "Test image does not exist."

        # Open the file in binary mode and send it as part of the request
        with open(image_path, "rb") as image_file:
            response = client.post(
                "/upload-image/",
                files={"file": ("test_image.jpg", image_file, "image/jpeg")},
            )

        # Assert the status code
        assert response.status_code == 200

        # Assert the response content
        response_json = response.json()
        assert response_json["filename"] == "test_image.jpg"
        assert response_json["status"] == "success"

    def test_csv_image(self):
        # Define the path to the test image
        csv_path = "data/purchase_data_sample.xlsx"

        # Make sure the file exists before running the test
        assert os.path.exists(csv_path), "Test image does not exist."

        # Open the file in binary mode and send it as part of the request
        with open(csv_path, "rb") as file:
            response = client.post(
                "/upload-csv/",
                files={"file": ("purchase_data_sample.xlsx", file, "text/csv")},
            )

        # Assert the status code
        assert response.status_code == 200

        # Assert the response content
        response_json = response.json()
        assert response_json["filename"] == "purchase_data_sample.xlsx"
        assert response_json["status"] == "success"

    def test_invalid_file_upload(self):
        # Simulate uploading a non-image file (e.g., a text file)
        text_file_content = b"This is not an image."
        response = client.post(
            "/upload-image/",
            files={"file": ("test_file.txt", text_file_content, "text/plain")},
        )

        # Assert that the server responds with a 400 error
        assert response.status_code == 400
        assert response.json() == {
            "detail": "Invalid file type. Please upload an image (jpeg, png, gif)."
        }


@pytest.mark.skipif(sys.version_info < (3, 8), reason="Requires Python 3.8 or later.")
class Test_Database_Queries_via_APIs:

    def test_database_connection(self):
        # the error will occur if the cursor is not defines
        conn = MySQL.connection
        assert conn is not None

        cursor = conn.cursor()
        assert cursor is not None

    def test_create_table(self):
        # create table
        MySQL.create_table(table_name=table_name, query=create_table_query)

    def check_item_database_response(self, response_json, data, id):
        """
        check the item content in the database and the server response are similar
        """
        # Assert that the response contains the correct item data
        assert response_json["id"] == id
        assert response_json["name"] == data["name"]
        assert response_json["description"] == data["description"]
        assert response_json["price"] == data["price"]

        # Check that the item was actually inserted into the database
        items = MySQL.search_for_sample(table_name=table_name, data=data)
        item = items[-1]
        assert item["id"] == id
        assert item["name"] == data["name"]
        assert item["description"] == data["description"]
        assert float(item["price"]) == float(data["price"])

    def create_item(self, data):
        # Send a POST request to the /create_items/ endpoint
        response = client.post("/items/", json=data)

        # Assert that the response status code is 200 OK
        assert response.status_code == 200
        response_json = response.json()
        id = response_json["id"]

        # check the item content in the database and the server response are similar
        self.check_item_database_response(response_json, data, id)

    def test_create_valid_item(self):
        self.create_item(valid_data)

    def create_invalid_item(self, data):
        # Send a POST request to the /create_items/ endpoint
        response = client.post("/items/", json=data)

        # Assert that the response status code is 200 OK
        assert response.status_code == 500

    def test_create_invalid_item(self):
        for data in invalid_data:
            self.create_invalid_item(data)

    def test_get_items(self):
        # Send a GET request to get all created items
        response = client.get("/items/")
        assert response.status_code == 200

    def test_update_items(self):
        # Send a POST request to the /create_items/ endpoint
        id=1
        response = client.put(f"/items/{id}", json=update_data)

        # Assert that the response status code is 200 OK
        # TODO : check the error :  404 = <Response [404 Not Found]>.status_code
        assert response.status_code == 200
        response_json = response.json()
        assert id == response_json["id"]

        # check the item content in the database and the server response are similar
        self.check_item_database_response(response_json, update_data, id)

    # def test_delete_table(self):
    #     # delete table
    #     MySQL.delete_table(table_name)
