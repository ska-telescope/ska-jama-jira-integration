"""
This module integrates with JIRA to manage and retrieve various requirement levels and
test cases.
"""

import pandas as pd

from ska_jama_jira_integration.jira.api_interface import (
    create_ticket,
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
        ticket (dict): The Jira ticket to extract the value from.
        jira_key (str): The key to access the desired field in the ticket.

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


def create_requirement(project_key, requirement_id, name, description, rationale):
    """
    Create a new requirement ticket in JIRA.
    """
    issue_type = "Requirement"
    priority = "Essential"
    jama_url = (
        "https://skaoffice.jamacloud.com/perspective.req?projectId=335&docId=900495"
    )
    verification_method = "Test"
    verification_milestones = "Unassigned"
    status = "REJECTED"

    optional_fields = {
        "description": description,
        "priority": {"name": priority},
        "customfield_12133": requirement_id,
        "customfield_13903": jama_url,
        "customfield_12137": rationale,
        "customfield_12149": [{"value": verification_method}],
        "customfield_15502": [{"value": verification_milestones}],
    }

    issue_response = create_ticket(project_key, issue_type, name, optional_fields)

    if issue_response:
        update_ticket_transitions(issue_response["key"], status)


def create_test_case(project_key, requirement_id, name, description):
    """
    Create a new test case ticket in JIRA.
    """
    issue_type = "Test"
    jama_url = (
        "https://skaoffice.jamacloud.com/perspective.req?projectId=335&docId=900495"
    )

    optional_fields = {}

    if requirement_id is not None:
        optional_fields["requirement_id"] = requirement_id

    if description is not None:
        optional_fields["description"] = description

    if jama_url is not None:
        optional_fields["customfield_13903"] = jama_url

    issue_response = create_ticket(project_key, issue_type, name, optional_fields)
    return issue_response
