"""
Configuration module for the FastAPI application.

This module is responsible for loading environment variables
and setting up logging configuration for the application.

Functions:
    load_dotenv(): Loads environment variables from a `.env` file.
    logging.basicConfig(): Configures logging settings for the application.
"""

import logging

from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Set up logging configuration
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
