# --------------------------------------------------------------------------------------------------
# --------------------------------------------------------------------------------------------------
import os
import sys

import pytest

sys.path
sys.path.append("src")

# --------------------------------------------------------------------------------------------------
# check if we are on GITHUB_ACTIONS
IN_GITHUB_ACTIONS = os.getenv("GITHUB_ACTIONS") == "true"
# Skip pytest if we are on GITHUB_ACTIONS
if IN_GITHUB_ACTIONS:
    pytest.skip(reason="Test doesn't work in Github Actions.", allow_module_level=True)


# --------------------------------------------------------------------------------------------------
def test_IN_GITHUB():
    pass


def test_example():
    assert True
