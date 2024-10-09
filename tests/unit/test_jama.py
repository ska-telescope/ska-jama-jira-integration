"""
Test the JAMA functions
"""

from unittest.mock import patch

from ska_jama_jira_integration import config  # noqa: F401  # pylint: disable=W0611
from ska_jama_jira_integration.jama.api_interface import get_l1_requirements
from ska_jama_jira_integration.jama.service import get_field_value


def test_get_l1_requirements_success():
    """
    Test that get_l1_requirements returns the expected list of L1 requirements.
    """
    mock_response_data = {
        "meta": {"pageInfo": {"totalResults": 2, "resultCount": 2}},
        "data": [
            {"id": 1, "name": "L1 Jama Requirement 1"},
            {"id": 2, "name": "L1 Jama Requirement 2"},
        ],
    }

    with patch("ska_jama_jira_integration.jama.api_interface.requests.get") as mock_get:
        mock_get.return_value.json.return_value = mock_response_data
        mock_get.return_value.status_code = 200

        # Test Jama  get_l1_requirements
        result = get_l1_requirements()

        assert isinstance(result, list)
        assert len(result) == 2
        assert result[0]["id"] == 1
        assert result[1]["name"] == "L1 Jama Requirement 2"


def test_get_field_value():  # noqa: E501
    """
    Test that get_field_value returns the expected value after transformation.
    """
    document = {
        "id": 899970,
        "documentKey": "SKAO-SYS_REQ-2671",
        "globalId": "666624",
        "project": 335,
        "fields": {
            "documentKey": "SKAO-SYS_REQ-2671",
            "name": "Receptor type",
            "description": "<p>Requirement description.</p>",
            "status": 8529,
            "allocation$1090": [11309],
            "compliant$1090": 11227,
            "compliance_rationale$1090": "<p>Requirement rational.</p>",
            "verification_method$1090": [11288],
            "verification_milestone$1090": [11463, 11459, 11470],
            "verification_compliance$1090": 11523,
            "tag$1090": "Low",
            "category$1090": "SKA-Low Configuration",
            "verification$1090": "Analysis",
            "allocation_to$1090": "LFAA",
            "globalId": "666624",
            "jira_url_address$1090": "https://jira.skatelescope.org/browse/L1-2278",
        },
    }

    jama_key = "documentKey"
    transformer = None
    value = get_field_value(document, jama_key, transformer)
    assert value == "SKAO-SYS_REQ-2671"
