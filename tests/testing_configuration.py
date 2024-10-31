# --------------------------------------------------------------------------------------------------
import os
import sys
import numpy as np
import pandas as pd
import pytest

sys.path
sys.path.append("src")
from utils.data_exploration import demo_preparation_modeling_pipelines



data_dict, stats_dict = demo_preparation_modeling_pipelines()
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
