"""
This module integrates with JAMA to manage and retrieve various requirement levels and
test cases.
"""

import pandas as pd

from ska_jama_jira_integration.jama.api_interface import (
    get_interfaces,
    get_item,
    get_l0_requirements,
    get_l1_requirements,
    get_l2_requirements,
    get_test_cases,
    put_item,
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


# pylint: disable=R0801
def extract_field_mapping_data(artifacts, mapping_type, product=None):
    """
    Extracts and maps JAMA artifacts based on a specified field mapping type.

    Args:
        - artifacts (list): A list of JAMA artifacts to be processed.
        - mapping_type (str): The type of field mapping to be used for extraction.
        - product (str): The product that needs to be added to the extracted data.

    Returns:
        list: A list of dictionaries containing the extracted and mapped data
    """

    # Load field mappings from YAML file
    field_mappings = get_field_mapping(mapping_type)

    # Extract data using field mappings
    extracted_data = []
    for artifact in artifacts:
        extracted_document = {}
        for field_mapping in field_mappings:
            field_name = field_mapping["name"]

            if "jama_field" in field_mapping:
                jama_field = field_mapping["jama_field"]
                if "key" in jama_field:
                    key = jama_field["key"]

                    transformer = None
                    if "transformer" in jama_field:
                        transformer = globals().get(jama_field["transformer"], None)

                    extracted_document[field_name] = get_field_value(
                        artifact, key, transformer
                    )

        if product:
            extracted_document["component"] = product

        extracted_data.append(extracted_document)

    return extracted_data


# pylint: enable=R0801


def get_jama_requirements(level: str, product: str) -> pd.DataFrame:
    """
    Retrieves Jama requirements for a given requirement level and product.

    Args:
        level (str): The requirement level ('L0', 'L1', 'L2'). product (str): The
        product identifier.

    Returns:
        pd.DataFrame: A DataFrame containing Jama requirements.
    """
    if level == "L0":
        jama_requirements = get_l0_requirements()
    elif level == "L1":
        jama_requirements = get_l1_requirements()
    elif level == "L2":
        jama_requirements = get_l2_requirements(product)
    else:
        raise ValueError(f"Unsupported level: {level}")

    if jama_requirements is None:
        raise ValueError("Failed to retrieve requirements from Jama.")

    extracted_data = extract_field_mapping_data(jama_requirements, "requirement")
    df = pd.DataFrame(extracted_data)
    return df


def get_jama_test_cases() -> pd.DataFrame:
    """
    Retrieves Jama test cases

    Returns:
        pd.DataFrame: A DataFrame containing the Jama test cases.
    """
    jama_test_cases = get_test_cases()

    if jama_test_cases is None:
        raise ValueError("Failed to retrieve test cases from Jama.")

    extracted_data = extract_field_mapping_data(jama_test_cases, "test_case")
    df = pd.DataFrame(extracted_data)
    return df


def get_jama_interfaces() -> pd.DataFrame:
    """
    Retrieves Jama interfaces

    Returns:
        pd.DataFrame: A DataFrame containing the Jama interfaces.
    """
    jama_interfaces = get_interfaces()

    if jama_interfaces is None:
        raise ValueError("Failed to retrieve interfaces from Jama.")

    extracted_data = extract_field_mapping_data(jama_interfaces, "interfaces")
    df = pd.DataFrame(extracted_data)
    return df


def update_jama_item(item_id, url):
    """
    Updates the jira url of an existing JAMA item.

    Args:
        item_id (int): The id of the jama item to be updated.
        url (str): The url to be set for the jama item.
    """
    item = get_item(id)
    item["fields"]["jira_url$1358"] = url
    put_item(item_id, item)
