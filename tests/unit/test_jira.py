"""
Test the JAMA functions
"""

from unittest.mock import patch

import requests

from ska_jama_jira_integration import config  # noqa: F401  # pylint: disable=W0611
from ska_jama_jira_integration.jira.api_interface import get_l1_requirements
from ska_jama_jira_integration.jira.service import create_requirement
from ska_jama_jira_integration.models.models import Requirement


def test_get_l1_requirements_success():
    mock_response_data = {
        "meta": {"pageInfo": {"totalResults": 2, "resultCount": 2}},
        "issues": [
            {"id": 1, "fields": {"name": "L1 Requirement 1"}},
            {"id": 2, "fields": {"name": "L1 Requirement 2"}},
        ],
    }

    with patch("ska_jama_jira_integration.jira.api_interface.requests.get") as mock_get:
        mock_get.return_value.json.return_value = mock_response_data
        mock_get.return_value.status_code = 200

        result = get_l1_requirements()

        assert isinstance(result, list)
        assert len(result) == 2
        assert result[0]["id"] == 1
        assert result[1]["fields"]["name"] == "L1 Requirement 2"


def test_create_requirements():
    requirement = Requirement(
        requirement_id="SKAO-SYS_REQ-2671",
        jama_url="jama_url",
        name="Receptor type",
        description="description",
        status="status",
        verification_method="verification_method",
        verification_milestones="verification_method",
        rationale="rationale",
        category="category",
        allocation="allocation",
        compliance="compliance",
        tags="tags",
        component="component",
    )

    # create_requirement("L1", requirement)
