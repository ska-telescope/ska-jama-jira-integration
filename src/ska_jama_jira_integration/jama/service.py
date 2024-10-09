"""
This module integrates with JAMA to manage and retrieve various requirement levels and
test cases.
"""

import pandas as pd

from ska_jama_jira_integration.jama.api_interface import (
    get_l0_requirements,
    get_l1_requirements,
    get_l2_requirements,
    get_test_cases,
)
from ska_jama_jira_integration.jama.transformers import *  # noqa: E501 F403 F401 # pylint: disable=W0401 W0614
from ska_jama_jira_integration.models.field_mapping import get_field_mapping


def get_field_value(document: dict, jama_key: str, transformer: callable = None):
    """
    Extracts the value from a document using a given Jama key and applies an optional
    transformer.

    Args:
        - document (dict): The Jama document to extract the value from.
        - jama_key (str): The key to access the desired field in the document.
        - transformer (callable, optional): A function to transform the extracted value.

    Returns:
        The extracted and possibly transformed value.
    """
    keys = jama_key.split(".")
    value = document
    for key in keys:
        value = value.get(key, None)

        if value is None:
            break

    # Execute transformer function
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
        requirements = get_l0_requirements()
    elif level == "L1":
        requirements = get_l1_requirements()
    elif level == "L2":
        requirements = get_l2_requirements(product)
    else:
        raise ValueError(f"Unsupported level: {level}")

    if requirements is None:
        raise ValueError("Failed to retrieve data from Jama.")

    # Extract data using field mappings
    extracted_requirements = []
    for document in requirements:
        extracted_document = {}
        for field in field_mappings:
            field_name = field["name"]
            jama_key = field["jama_key"]
            transformer = globals().get(field.get("transformer"), None)
            extracted_document[field_name] = get_field_value(
                document, jama_key, transformer
            )
        extracted_document["component"] = product
        extracted_requirements.append(extracted_document)

    return pd.DataFrame(extracted_requirements)


def get_jama_test_cases() -> pd.DataFrame:
    """
    Retrieves Jama test cases

    Returns:
        pd.DataFrame: A DataFrame containing the Jama test cases.
    """
    # Load field mappings from YAML file
    field_mappings = get_field_mapping("test_case")
    test_cases = get_test_cases()

    if test_cases is None:
        raise ValueError("Failed to retrieve data from Jama.")

    # Extract data using field mappings
    extracted_test_cases = []
    for document in test_cases:
        extracted_document = {}
        for field in field_mappings:
            field_name = field["name"]
            jama_key = field["jama_key"]
            transformer = globals().get(field.get("transformer"), None)
            extracted_document[field_name] = get_field_value(
                document, jama_key, transformer
            )
        extracted_test_cases.append(extracted_document)

    return pd.DataFrame(extracted_test_cases)
