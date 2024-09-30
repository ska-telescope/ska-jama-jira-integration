"""
This module integrates with JAMA to manage and retrieve various requirement levels and
test cases.
"""

import pandas as pd

from jama.jama_inferface import (
    get_l0_requirements,
    get_l1_requirements,
    get_l2_requirements,
    get_test_cases,
)
from ska_jama_jira_integration.jama.transformers import *
from models.field_mapping import get_field_mapping


def get_field_value(document: dict, jama_key: str, transformer: callable = None):
    """
    Extracts the value from a document using a given Jama key and applies an optional
    transformer.

    Args:
        document (dict): The Jama document to extract the value from. jama_key (str):
        The key to access the desired field in the document. transformer (callable,
        optional): A function to transform the extracted value.

    Returns:
        The extracted and possibly transformed value.
    """
    keys = jama_key.split(".")
    value = document
    for key in keys:
        value = value.get(key, None)
        if value is None:
            break
    if transformer:
        return transformer(value)
    return value


def get_jama_requirements(level: str, product: str) -> pd.DataFrame:
    """
    Retrieves Jama requirements for a given requirement level and product.

    Args:
        level (str): The requirement level ('L0', 'L1', 'L2'). product (str): The
        product identifier.

    Returns:
        pd.DataFrame: A DataFrame containing Jama requirements.
    """
    # Load field mappings from YAML file
    field_mappings = get_field_mapping("requirement")

    # Retrieve data based on the requirement level
    if level == "L0":
        data = get_l0_requirements()
    elif level == "L1":
        data = get_l1_requirements()
    elif level == "L2":
        data = get_l2_requirements(product)
    else:
        raise ValueError(f"Unsupported level: {level}")

    if data is None:
        raise ValueError("Failed to retrieve data from Jama.")

    # Extract data using field mappings
    extracted_data = []
    for document in data:
        extracted_document = {}
        for field in field_mappings:
            field_name = field["name"]
            jama_key = field["jama_key"]
            transformer = globals().get(field.get("transformer"), None)
            extracted_document[field_name] = get_field_value(
                document, jama_key, transformer
            )
        extracted_document["component"] = product
        extracted_data.append(extracted_document)

    return pd.DataFrame(extracted_data)


def get_jama_test_cases() -> pd.DataFrame:
    """
    Retrieves Jama test cases

    Returns:
        pd.DataFrame: A DataFrame containing the Jama test cases.
    """
    # Load field mappings from YAML file
    field_mappings = get_field_mapping("test_case")
    data = get_test_cases()

    if data is None:
        raise ValueError("Failed to retrieve data from Jama.")

    # Extract data using field mappings
    extracted_data = []
    for document in data:
        extracted_document = {}
        for field in field_mappings:
            field_name = field["name"]
            jama_key = field["jama_key"]
            transformer = globals().get(field.get("transformer"), None)
            extracted_document[field_name] = get_field_value(
                document, jama_key, transformer
            )
        extracted_data.append(extracted_document)

    return pd.DataFrame(extracted_data)
