# Prepare the data for the new item

valid_data = {
    "name": "user",
    "description": "This is a test description",
    "price": 12.3,
}
update_data = {  # update product id=0 with
    "name": "user2",
    "description": "This is a test description [updated]",
    "price": 1236.5,
}

invalid_data = [
    {
        "name": "user3",
        "description": 12,
        "price": 5e40, #DECIMAL(10, 2): max 10 digits
    },
]
