"""
JAMA - JIRA Integration
"""

import argparse
import logging
import sys

from ska_jama_jira_integration import config  # noqa: F401  # pylint: disable=W0611
from ska_jama_jira_integration.services.synchronize import (  # noqa: F401
    sync_l1,
    sync_l2,
    sync_test_cases,
)


def main():
    parser = argparse.ArgumentParser(
        description="JIRA and JAMA Synchronization Service"
    )
    parser.add_argument(
        "--sync",
        type=str,
        choices=["all", "l1", "l2", "test_cases"],
        help="Specify what to sync: all, l1, l2, test_cases",
    )

    args = parser.parse_args()

    if args.sync == "all":
        sync_l1()
        sync_l2()
        sync_test_cases()
    elif args.sync == "l1":
        sync_l1()
    elif args.sync == "l2":
        sync_l2()
    elif args.sync == "test_cases":
        sync_test_cases()
    else:
        logging.info("No valid sync option provided.")


if __name__ == "__main__":
    main()
