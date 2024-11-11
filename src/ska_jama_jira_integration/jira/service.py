"""
This module integrates with JIRA to manage and retrieve various requirement levels and
test cases.
"""

import re

import pandas as pd

from ska_jama_jira_integration.jira.api_interface import (
    create_ticket,
    get_interfaces,
    get_l1_requirements,
    get_l2_requirements,
    get_test_cases,
    update_ticket_transitions,
)
from ska_jama_jira_integration.models.field_mapping import get_field_mapping


def get_field_value(ticket: dict, jira_key: str):
    """
    Extracts the value from a document using a given Jira key.

    Args:
        - ticket (dict): The Jira ticket to extract the value from.
        - jira_key (str): The key to access the desired field in the ticket.

    Returns:
        The extracted value.
    """
    keys = jira_key.split(".")
    value = ticket
    for key in keys:
        value = value.get(key, None)

        if value is None:
            break

    if isinstance(value, list) and len(value) > 0:
        concatenated_values = ",".join([item.get("value", "") for item in value])
        value = concatenated_values

    return value


# pylint: disable=R0801
def extract_field_mapping_data(artifacts, mapping_type):
    """
    Extracts and maps JIRA artifacts based on a specified field mapping type.

    Args:
        - artifacts (list): A list of JIRA artifacts to be processed.
        - mapping_type (str): The type of field mapping to be used for extraction.

    Returns:
        list: A list of dictionaries containing the extracted and mapped data
    """

    # Load field mappings from YAML file
    field_mappings = get_field_mapping(mapping_type)

    # Extract data into field mappings
    extracted_data = []
    for artifact in artifacts:
        extracted_document = {}
        for field_mapping in field_mappings:
            field_name = field_mapping["name"]

            if "jira_field" in field_mapping:
                jira_field = field_mapping["jira_field"]
                if "key" in jira_field:
                    key = jira_field["key"]
                    extracted_document[field_name] = get_field_value(artifact, key)

        extracted_data.append(extracted_document)

    return extracted_data


# pylint: enable=R0801


def get_jira_requirements(level) -> pd.DataFrame:
    """
    Retrieves JIRA requirements for a given requirement level.

    Args:
        level (str): The requirement level ('L0', 'L1', 'L2').

    Returns:
        pd.DataFrame: A DataFrame containing Jira requirements.
    """
    if level == "L1":
        jira_requirements = get_l1_requirements()
    elif level == "L2":
        jira_requirements = get_l2_requirements()
    else:
        raise ValueError(f"Unsupported level: {level}")

    if jira_requirements is None:
        raise ValueError("Failed to retrieve requirements from JIRA.")

    extracted_data = extract_field_mapping_data(jira_requirements, "requirement")
    df = pd.DataFrame(extracted_data)
    return df


def get_jira_test_cases() -> pd.DataFrame:
    """
    Retrieves JIRA test cases.

    Returns:
        pd.DataFrame: A DataFrame containing the Jira test cases
    """
    jira_test_cases = get_test_cases()

    if jira_test_cases is None:
        raise ValueError("Failed to retrieve test cases from JIRA.")

    extracted_data = extract_field_mapping_data(jira_test_cases, "test_case")
    df = pd.DataFrame(extracted_data)
    return df


def get_jira_interfaces() -> pd.DataFrame:
    """
    Retrieves JIRA test cases.

    Returns:
        pd.DataFrame: A DataFrame containing the Jira test cases
    """
    jira_interfaces = get_interfaces()

    if jira_interfaces is None:
        raise ValueError("Failed to retrieve interfaces from JIRA.")

    extracted_data = extract_field_mapping_data(jira_interfaces, "test_case")
    df = pd.DataFrame(extracted_data)
    return df


def create_requirement(project_key, requirement):
    """
    Create a new requirement ticket in JIRA.
    """
    issue_type = "Requirement"
    priority = "Essential"

    optional_fields = {
        "priority": {"name": priority},
    }

    field_mappings = get_field_mapping("requirement")
    for field_mapping in field_mappings:
        field_name = field_mapping["name"]

        if "jira_field" in field_mapping:
            jira_field = field_mapping["jira_field"]
            if "key" in jira_field:
                key = jira_field["key"]  # e.g: fields.customfield_13903

                # Remove field. from the jira_key
                if key.startswith("fields."):
                    key = key[len("fields.") :]  # noqa: E203

                # Get value from requirement
                value = requirement.get(field_name)
                if value:
                    set_optional_field_value(jira_field, key, value, optional_fields)

    # Create jira ticket
    issue_response = create_ticket(
        project_key, issue_type, requirement.get("name"), optional_fields
    )

    # Update jira ticket status
    if issue_response:
        update_ticket_transitions(issue_response["key"], requirement.get("status"))


def set_optional_field_value(jira_field, key, value, optional_fields):
    """
    Set the value of an optional field based on its type.
    """
    field_type = jira_field.get("type")
    if field_type == "array":
        split_values = re.split(";", value)
        optional_fields[key] = [{"value": v} for v in split_values]
    elif field_type == "radio":
        optional_fields[key] = {"value": value}
    else:
        optional_fields[key] = value


def create_test_case(project_key, test_case):
    """
    Create a new test case ticket in JIRA.
    """
    issue_type = "Test"

    optional_fields = {}

    field_mappings = get_field_mapping("test_case")
    for field in field_mappings:
        field_name = field.get("name")
        jira_key = field.get("jira_key")

        if jira_key:
            # Remove field. from the jira_key
            if jira_key and jira_key.startswith("fields."):
                jira_key = jira_key[len("fields.") :]  # noqa: E203

            # Get value from test case
            value = test_case.get(field_name)
            if value:
                if field.get("jira_is_array", False):
                    optional_fields[jira_key] = [{"value": value}]
                elif field.get("jira_is_radio", False):
                    optional_fields[jira_key] = {"value": value}
                else:
                    optional_fields[jira_key] = value

    # Create jira ticket
    issue_response = create_ticket(
        project_key, issue_type, test_case.get("name"), optional_fields
    )

    # Update jira ticket status
    if issue_response:
        update_ticket_transitions(issue_response["key"], test_case.get("status"))


def create_interface(project_key, interface):
    """
    Create a new interface ticket in JIRA.
    """
    issue_type = "Interface"

    optional_fields = {
        "components": [{"name": "Testing Infrastructure"}],
    }

    field_mappings = get_field_mapping("interfaces")
    for field in field_mappings:
        field_name = field.get("name")
        jira_key = field.get("jira_key")

        if jira_key:
            # Remove field. from the jira_key
            if jira_key and jira_key.startswith("fields."):
                jira_key = jira_key[len("fields.") :]  # noqa: E203

            # Get value from interface
            value = interface.get(field_name)
            if value:
                if field.get("jira_is_array", False):
                    optional_fields[jira_key] = [{"value": value}]
                elif field.get("jira_is_radio", False):
                    optional_fields[jira_key] = {"value": value}
                else:
                    optional_fields[jira_key] = value

    # Create jira ticket
    issue_response = create_ticket(
        project_key, issue_type, interface.get("name"), optional_fields
    )

    # Update jira ticket status
    if issue_response:
        update_ticket_transitions(issue_response["key"], interface.get("status"))

    return issue_response
