# --------------------------------------------------------------------------------------------------
import sys

sys.path
sys.path.append("src")

from utils.data_exploration import demo_preparation_modeling_pipelines

if __name__ == "__main__":
    # Build the response dictionary
    demo_preparation_modeling_pipelines()
