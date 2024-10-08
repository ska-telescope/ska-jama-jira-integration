"""
This module interacts with the JIRA API to fetch various requirement levels (L0, L1, L2)
and test cases.
"""

import logging
import os
from typing import Any, Dict, List, Optional

import requests

from ska_jama_jira_integration.models.field_mapping import get_field_mapping

# Get and validate environment variables
JIRA_TOKEN = os.getenv("JIRA_TOKEN")
JIRA_BASEURL = os.getenv("JIRA_BASEURL")

if not JIRA_TOKEN or not JIRA_BASEURL:
    raise EnvironmentError(
        """One or more required environment variables
        (JIRA_TOKEN, JIRA_BASEURL) are not set."""
    )


def fetch_paginated_results(api_url: str) -> List[Dict[str, Any]]:
    """
    Fetches all paginated results from the provided JIRA API URL.

    Args:
        api_url (str): The base API URL for the request.

    Returns:
        List[Dict[str, Any]]: A list of all data items retrieved from the API.
    """
    all_data = []
    start_at = 0
    max_results = 500

    headers = {
        "Authorization": f"Bearer {JIRA_TOKEN}",
        "Content-Type": "application/json",
    }

    while True:
        paginated_url = f"{api_url}&startAt={start_at}&maxResults={max_results}"
        logging.info("Fetching Jira data from: %s", paginated_url)

        try:
            response = requests.get(paginated_url, headers=headers, timeout=10)
            response.raise_for_status()
        except requests.exceptions.RequestException as e:
            logging.error("Failed to retrieve data from JIRA: %s", e)
            raise

        result = response.json()
        data = result.get("issues", [])
        all_data.extend(data)

        # Update pagination details from the response
        total_results = result.get("total", 0)
        start_at += result.get("maxResults", 0)

        # Break the loop if all results are fetched
        if start_at >= total_results:
            break

    return all_data


def make_jira_request(filter_id: int, mapping_type: str) -> Optional[Dict[str, Any]]:
    """
    Makes a request to the JIRA API with the specified filter ID.

    Args:
        filter_id (int): The filter ID to be used in the JQL query.

    Returns:
        Optional[Dict[str, Any]]: The JSON response from the JIRA API, or None if an
        error occurs.
    """
    # Get field mapping and create filter
    field_mappings = get_field_mapping(mapping_type)
    jira_fields = [
        field["jira_key"].replace("fields.", "")
        for field in field_mappings
        if "jira_key" in field
    ]

    api_url = f"{JIRA_BASEURL}/search"
    params = {
        "jql": f"filter={filter_id}",
        "fields": jira_fields,
    }

    try:
        params["fields"] = ",".join(params["fields"])

        query_params = "&".join([f"{key}={value}" for key, value in params.items()])
        full_url = f"{api_url}?{query_params}"
        return fetch_paginated_results(full_url)
    except requests.exceptions.RequestException as e:
        logging.error("Failed to retrieve data from JIRA: %s", e)
        return None


def get_l1_requirements() -> Optional[Dict[str, Any]]:
    """
    Retrieves the level 1 requirements from JIRA.

    Returns:
        Optional[Dict[str, Any]]: The JSON response from the JIRA API, or None if an
        error occurs.
    """
    return make_jira_request(filter_id=18234, mapping_type="requirement")


def get_l2_requirements() -> Optional[Dict[str, Any]]:
    """
    Retrieves the level 2 requirements from JIRA.

    Returns:
        Optional[Dict[str, Any]]: The JSON response from the JIRA API, or None if an
        error occurs.
    """
    return make_jira_request(filter_id=18132, mapping_type="requirement")


def get_test_cases() -> Optional[Dict[str, Any]]:
    """
    Retrieves the test cases from JIRA.

    Returns:
        Optional[Dict[str, Any]]: The JSON response from the JIRA API, or None if an
        error occurs.
    """
    return make_jira_request(filter_id=18807, mapping_type="test_case")


def create_ticket(
    project_key, issue_type, summary, optional_fields=None
) -> Optional[Dict[str, Any]]:
    """
    Creates a new ticket in JIRA.

    Args:
        project_key (str): The key of the project in which to create the ticket.
        issue_type (str): The type of issue. summary (str): A brief summary of the
        ticket. optional_fields (Optional[Dict[str, Any]]): Additional fields for the
        ticket (optional).

    Returns:
        Optional[Dict[str, Any]]: The JSON response from JIRA with ticket details if
        successful, or None if an error occurs.
    """
    api_url = f"{JIRA_BASEURL}/issue"
    headers = {
        "Authorization": f"Bearer {JIRA_TOKEN}",
        "Content-Type": "application/json",
    }

    # Construct the payload with the mandatory fields
    issue_data = {
        "fields": {
            "project": {"key": project_key},
            "issuetype": {"name": issue_type},
            "summary": summary,
        }
    }
    print(issue_data)

    # Optionally fields if provided
    if optional_fields:
        issue_data["fields"].update(optional_fields)

    try:
        response = requests.post(api_url, headers=headers, json=issue_data, timeout=10)
        response.raise_for_status()
        logging.info("Successfully created Jira ticket for %s", summary)
        return response.json()
    except requests.exceptions.RequestException as e:
        logging.error("Failed to create ticket in Jira: %s", e)
        return None


def update_ticket_transitions(issue_key, status):
    """
    Updates the status of an existing JIRA ticket by transitioning it to a new status.

    Args:
        issue_key (str): The key of the ticket to be updated.
        status (str): The new status to which the ticket should be transitioned.
    """
    api_url = f"{JIRA_BASEURL}/issue/{issue_key}/transitions"
    headers = {
        "Authorization": f"Bearer {JIRA_TOKEN}",
        "Content-Type": "application/json",
    }

    try:
        transition_id = get_ticket_transitions(issue_key, status)
        issue_data = {"transition": {"id": transition_id}}

        response = requests.post(api_url, headers=headers, json=issue_data, timeout=10)
        response.raise_for_status()
        logging.info("Successfully updated Jira ticket transition for %s", issue_key)
    except requests.exceptions.RequestException as e:
        logging.error("Failed to update ticket transition in JIRA: %s", e)


def get_ticket_transitions(issue_key, status):
    """
    Retrieves the transition ID for a given status from JIRA, used for transitioning a
    ticket.

    Args:
        issue_key (str): The key of the ticket whose transitions are to be retrieved.
        status (str): The name of the status for which the transition ID is needed.

    Returns:
        Optional[str]: The transition ID corresponding to the status, or None if not
        found or an error occurs.
    """
    api_url = f"{JIRA_BASEURL}/issue/{issue_key}/transitions"
    headers = {
        "Authorization": f"Bearer {JIRA_TOKEN}",
        "Content-Type": "application/json",
    }

    try:
        response = requests.get(api_url, headers=headers, timeout=10)
        if response.status_code == 200:
            transitions = response.json()["transitions"]
            transition_id = None
            for transition in transitions:
                if transition["name"] == status:
                    transition_id = transition["id"]
                    break

        return transition_id
    except requests.exceptions.RequestException as e:
        logging.error("Failed to update ticket transition in JIRA: %s", e)
        return None
