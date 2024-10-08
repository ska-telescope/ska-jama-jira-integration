"""
Test the JAMA functions
"""

from unittest.mock import patch

from ska_jama_jira_integration import config  # noqa: F401  # pylint: disable=W0611
from ska_jama_jira_integration.jama.api_interface import get_l1_requirements


def test_get_l1_requirements_success():
    mock_response_data = {
        "meta": {"pageInfo": {"totalResults": 2, "resultCount": 2}},
        "data": [
            {"id": 1, "name": "L1 Requirement 1"},
            {"id": 2, "name": "L1 Requirement 2"},
        ],
    }

    with patch("ska_jama_jira_integration.jama.api_interface.requests.get") as mock_get:
        mock_get.return_value.json.return_value = mock_response_data
        mock_get.return_value.status_code = 200

        result = get_l1_requirements()

        assert isinstance(result, list)
        assert len(result) == 2
        assert result[0]["id"] == 1
        assert result[1]["name"] == "L1 Requirement 2"


# def test_get_l1_requirements_failure():
#     with patch(
#         "ska_jama_jira_integration.jama.jama_interface.requests.get"
#     ) as mock_get:
#         mock_get.return_value.raise_for_status.side_effect = (
#             requests.exceptions.HTTPError
#         )

#         try:
#             get_l1_requirements()
#             assert False, "Expected an HTTPError but none was raised."
#         except requests.exceptions.HTTPError:
#             assert True
