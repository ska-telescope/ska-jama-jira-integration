"""
This module integrates with JIRA to manage and retrieve various requirement levels and
test cases.
"""

import pandas as pd
import re

from ska_jama_jira_integration.jira.api_interface import (
    create_ticket,
    get_l1_requirements,
    get_l2_requirements,
    get_test_cases,
    get_interfaces,
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
        # value = value[0].get("value", None)

    return value


def get_jira_requirements(level) -> pd.DataFrame:
    """
    Retrieves JIRA requirements for a given requirement level.

    Args:
        level (str): The requirement level ('L0', 'L1', 'L2').

    Returns:
        pd.DataFrame: A DataFrame containing Jira requirements.
    """
    # Load field mappings from YAML file
    field_mappings = get_field_mapping("requirement")

    if level == "L1":
        data = get_l1_requirements()
    elif level == "L2":
        data = get_l2_requirements()
    else:
        raise ValueError(f"Unsupported level: {level}")

    if data is None:
        raise ValueError("Failed to retrieve data from JIRA.")

    # extracted_data = [
    #     {
    #         "id": issue["id"],
    #         "key": issue["key"],
    #         "document_id": issue["fields"]["customfield_12133"],
    #         "name": issue["fields"]["summary"],
    #         "description": issue["fields"]["description"],
    #     }
    #     for issue in data
    # ]

    extracted_data = []
    for ticket in data:
        extracted_document = {}
        for field in field_mappings:
            field_name = field["name"]
            if field.get("jira_key", None):
                jira_key = field["jira_key"]
                extracted_document[field_name] = get_field_value(ticket, jira_key)
        extracted_data.append(extracted_document)

    df = pd.DataFrame(extracted_data)
    return df


def get_jira_test_cases() -> pd.DataFrame:
    """
    Retrieves JIRA test cases.

    Returns:
        pd.DataFrame: A DataFrame containing the Jira test cases
    """
    # Load field mappings from YAML file
    field_mappings = get_field_mapping("test_case")

    data = get_test_cases()

    if data is None:
        raise ValueError("Failed to retrieve data from JIRA.")

    extracted_data = []
    for ticket in data:
        extracted_document = {}
        for field in field_mappings:
            field_name = field["name"]
            if field.get("jira_key", None):
                jira_key = field["jira_key"]
                extracted_document[field_name] = get_field_value(ticket, jira_key)
        extracted_data.append(extracted_document)

    df = pd.DataFrame(extracted_data)
    return df


def get_jira_interfaces() -> pd.DataFrame:
    """
    Retrieves JIRA test cases.

    Returns:
        pd.DataFrame: A DataFrame containing the Jira test cases
    """
    # Load field mappings from YAML file
    field_mappings = get_field_mapping("interfaces")

    data = get_interfaces()

    if data is None:
        raise ValueError("Failed to retrieve data from JIRA.")

    extracted_data = []
    for ticket in data:
        extracted_document = {}
        for field in field_mappings:
            field_name = field["name"]
            if field.get("jira_key", None):
                jira_key = field["jira_key"]
                extracted_document[field_name] = get_field_value(ticket, jira_key)
        extracted_data.append(extracted_document)

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
    for field in field_mappings:
        field_name = field.get("name")
        jira_key = field.get("jira_key")

        if jira_key:
            # Remove field. from the jira_key
            if jira_key and jira_key.startswith("fields."):
                jira_key = jira_key[len("fields.") :]

            # Get value from requirement
            value = requirement.get(field_name)
            if value:
                if field.get("jira_is_array", False):
                    split_values = re.split(r",\s*(?![^()]*\))", value)
                    values_list = [
                        {
                            "value": (
                                "Unassigned" if v.strip() == "UNASSIGNED" else v.strip()
                            )
                        }
                        for v in split_values
                    ]

                    optional_fields[jira_key] = values_list
                else:
                    optional_fields[jira_key] = value

    # Create jira ticket
    issue_response = create_ticket(
        project_key, issue_type, requirement.get("name"), optional_fields
    )

    # Update jira ticket status
    if issue_response:
        update_ticket_transitions(issue_response["key"], requirement.get("status"))


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
                jira_key = jira_key[len("fields.") :]

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
                jira_key = jira_key[len("fields.") :]

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
