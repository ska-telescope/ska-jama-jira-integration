"""
JAMA - JIRA Integration
"""

import logging

# pylint: disable=C0413
from dotenv import load_dotenv

load_dotenv()

from ska_jama_jira_integration.services.synchronize import sync_l1  # noqa: E402

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)


if __name__ == "__main__":
    logging.info("Sync started")

    sync_l1()
    # sync_l2()
    # sync_test_cases()
