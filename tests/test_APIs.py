###------------------------------------------------------------------------------------------------
import os

import pytest

# check if we are on GITHUB_ACTIONS
IN_GITHUB_ACTIONS = os.getenv("GITHUB_ACTIONS") == "true"


# Skip pytest if we are on GITHUB_ACTIONS
def test_IN_GITHUB():
    assert 1==1


if True:  # not not IN_GITHUB_ACTIONS:
    pytest.skip(reason="Test doesn't work in Github Actions.", allow_module_level=True)
###------------------------------------------------------------------------------------------------

import sys

sys.path
sys.path.append("webapp")
from fastapi.testclient import TestClient

from webapp import app

# Instantiate the client
client = TestClient(app)
print(f" root={os.getcwd()}")
table_name = "demo"


class Test_Dashboard_APIs:
    # def test_database_connection(self):
    #     try:
    #         # the error will occur if the cursor is not defines
    #         conn = MySQL.connection
    #         cursor = conn.cursor()
    #     except:
    #         assert conn != None

    # def test_create_table(self):
    #     # create table
    #     if does_table_Exists(table_name):
    #         err = create_table(table_name)
    #         assert err == 0

    # def test_delete_table(self):
    #     # delete table
    #     if not does_table_Exists(table_name):
    #         err = delete_table(table_name)
    #         assert err == 0

    def test_create_item(self):
        # Prepare the data for the new item
        data = {
            "name": "Test Item",
            "description": "This is a test description",
            "price": 5,
        }

        # Send a POST request to the /items/ endpoint
        response = client.post("/items/", params=data)

        # Assert that the response status code is 200 OK
        assert response.status_code == 200

        # Assert that the response contains the correct item data
        response_json = response.json()
        assert response_json["name"] == data["name"]
        assert response_json["description"] == data["description"]
        assert response_json["price"] == data["price"]

        # TODO: update the MySQL database
        # Check that the item was actually inserted into the database
        # with TestingSessionLocal() as db:
        #     item_in_db = db.query(Item).filter(Item.name == data["name"]).first()
        #     assert item_in_db is not None
        #     assert item_in_db.name == data["name"]
        #     assert item_in_db.description == data["description"]

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
        assert response_json["message"] == "Image uploaded successfully"

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
