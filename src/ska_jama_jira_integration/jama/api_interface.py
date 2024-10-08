"""
This module interacts with the JAMA API to fetch various requirement levels (L0, L1, L2)
and test cases.
"""

import logging
import os
from typing import Any, Dict, List, Optional

import requests
from requests.auth import HTTPBasicAuth

# Get and validate environment variables
JAMA_BASEURL = os.getenv("JAMA_BASEURL")
JAMA_USER = os.getenv("JAMA_USER")
JAMA_PASSWORD = os.getenv("JAMA_PASSWORD")

if not JAMA_BASEURL or not JAMA_USER or not JAMA_PASSWORD:
    raise EnvironmentError(
        """One or more required environment variables
        (JAMA_BASEURL, JAMA_USER, JAMA_PASSWORD) are not set."""
    )

# Use HTTPBasicAuth for authentication
auth = HTTPBasicAuth(JAMA_USER, JAMA_PASSWORD)


PRODUCT_URLS = {
    "TMC": "2192",
    "OSO": "2193",
    "SDP": "2194",
    "PLATFORM": "2195",
    "LOW CSP": "2196",
    "LOW PSS": "2367",
    "LOW PST": "2368",
    "LOW CBF": "2366",
    "LOW CSP LMC": "2369",
    "LOW SPS": "2191",
    "LOW ANTENNA ASSEMBLY": "2190",
    "MID CSP": "2197",
    "MID CSP LMC": "2375",
    "MID CBF": "2372",
    "MID PSS": "2373",
    "MID PST": "2374",
    "DSH LMC": "2198",
    "DSH ELEMENT": "2213",
    "BAND 1": "2200",
    "BAND 2": "2201",
    "BAND 5": "2202",
    "SPF SERVICES": "2203",
    "CRYO": "2204",
    "LFAA": "2205",
    "MCCS": "2370",
    "FIELD NODE": "2371",
    "LOW NETWORKS": "2206",
    "LOW INAU": "2207",
    "LOW PASD": "2208",
    "SAT": "2209",
    "MID INSA": "2210",
    "MID NETWORKS": "2211",
    "MID SPFRx": "2212",
    "DSH STRUCTURE": "2199",
    "MID INFRA": "2214",
    "MID SAT.STFR.FRQ": "2215",
    "MID AA0.5 BAND 5 DOWNCONVERTER": "2216",
}


def get_url(product: str) -> Optional[str]:
    """
    Constructs the appropriate JAMA API URL based on the product.

    Args:
        product (str): The product identifier.

    Returns:
        Optional[str]: The constructed URL, or None if the product is not recognized.
    """
    filter_id = PRODUCT_URLS.get(product)
    if filter_id:
        return f"{JAMA_BASEURL}/filters/{filter_id}/results"

    logging.warning("Product %s not recognized.", product)
    return None


def fetch_paginated_results(api_url: str) -> List[Dict[str, Any]]:
    """
    Fetches all paginated results from the provided JAMA API URL.

    Args:
        api_url (str): The base API URL for the request.

    Returns:
        List[Dict[str, Any]]: A list of all data items retrieved from the API.
    """
    all_data = []
    start_at = 0
    max_results = 50

    while True:
        paginated_url = f"{api_url}?startAt={start_at}&maxResults={max_results}"
        logging.info("Fetching Jama data from: %s", paginated_url)

        try:
            response = requests.get(paginated_url, auth=auth, timeout=10)
            response.raise_for_status()
        except requests.exceptions.RequestException as e:
            logging.error("Failed to retrieve data from JAMA: %s", e)
            raise

        result = response.json()
        data = result.get("data", [])
        all_data.extend(data)

        # Pagination details
        page_info = result.get("meta", {}).get("pageInfo", {})
        total_results = page_info.get("totalResults", 0)
        result_count = page_info.get("resultCount", 0)

        # Update start_at for the next page
        start_at += result_count

        # Break the loop if we have retrieved all results
        if start_at >= total_results:
            break

    return all_data


def get_l0_requirements() -> List[Dict[str, Any]]:
    """
    Retrieves all L0 requirements from JAMA by fetching all paginated results.

    Returns:
        List[Dict[str, Any]]: A list of all L0 data items retrieved from the API.
    """
    api_url = f"{JAMA_BASEURL}/filters/2082/results"
    return fetch_paginated_results(api_url)


def get_l1_requirements() -> List[Dict[str, Any]]:
    """
    Retrieves all L1 requirements from JAMA by fetching all paginated results.

    Returns:
        List[Dict[str, Any]]: A list of all L1 data items retrieved from the API.
    """
    api_url = f"{JAMA_BASEURL}/filters/2087/results"
    return fetch_paginated_results(api_url)


def get_l2_requirements(product: str) -> Optional[List[Dict[str, Any]]]:
    """
    Retrieves all L2 requirements from JAMA by fetching all paginated results.

    Args:
        product (str): The product identifier.

    Returns:
        Optional[List[Dict[str, Any]]]: A list of all L2 data items retrieved from the
        API, or None if an error occurs.
    """
    api_url = get_url(product)
    if api_url:
        return fetch_paginated_results(api_url)
    return None


def get_test_cases() -> Optional[List[Dict[str, Any]]]:
    """
    Retrieves all Test Cases from JAMA by fetching all paginated results.

    Returns:
        Optional[List[Dict[str, Any]]]: A list of all test cases retrieved from the API,
        or None if an error occurs.
    """
    api_url = f"{JAMA_BASEURL}/filters/2364/results"
    return fetch_paginated_results(api_url)
