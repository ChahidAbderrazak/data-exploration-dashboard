import yaml
from fastapi import FastAPI
from fastapi.responses import JSONResponse

app = FastAPI()

# Load OpenAPI spec from swagger.yaml
with open("swagger.yaml", "r") as f:
    swagger_spec = yaml.safe_load(f)

# Sample data for demonstration
items = [
    {"id": 1, "name": "Item One"},
    {"id": 2, "name": "Item Two"},
]


# Override FastAPI's OpenAPI method to use the external YAML file
@app.get("/get-swagger")
def custom_openapi():
    return JSONResponse(swagger_spec)


# API Endpoints
@app.get("/items")
def get_items():
    return items


@app.get("/items/{item_id}")
def get_item(item_id: int):
    item = next((item for item in items if item["id"] == item_id), None)
    if item:
        return item
    return {"error": "Item not found"}, 404


# Root endpoint
@app.get("/")
def root():
    return {"message": "Hello World!"}
