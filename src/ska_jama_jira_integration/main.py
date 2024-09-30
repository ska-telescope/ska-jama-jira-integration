"""
JAMA - JIRA Integration
"""

import logging

from ska_jama_jira_integration.services.synchronize import sync_l2  # noqa: E402

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)


if __name__ == "__main__":
    logging.info("Sync started")

    # sync_l1()
    sync_l2()
    # sync_test_cases()
