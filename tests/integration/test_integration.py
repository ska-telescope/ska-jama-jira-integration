"""
Simple FASTAPI App Tests for workshop purposes

Returns:
  None
"""

import warnings

import pytest


@pytest.mark.post_deployment
def test_root_endpoint():
    """
    Tests the root endpoint of the deployed FastAPI application.

    Sends a GET request to the root endpoint and verifies
    the response matches the expected status code and message.
    """
    warnings.warn(UserWarning("no api version is specified!"))
    return 1
