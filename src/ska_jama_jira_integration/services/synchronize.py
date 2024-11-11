"""
Synchronize JIRA and JAMA dataframes
"""

import logging

import pandas as pd

from ska_jama_jira_integration.jama.service import (
    get_jama_interfaces,
    get_jama_requirements,
    get_jama_test_cases,
)
from ska_jama_jira_integration.jira.service import (
    create_interface,
    create_requirement,
    create_test_case,
    get_jira_interfaces,
    get_jira_requirements,
    get_jira_test_cases,
)


def compare_dataframes(df1, df2):
    """
    Compare two dataframes and return new, removed, and modified entries.
    """
    new_entries = df2[~df2.index.isin(df1.index)]
    removed_entries = df1[~df1.index.isin(df2.index)]

    common_ids = df1.index.intersection(df2.index)
    df1_common = df1.loc[common_ids]
    df2_common = df2.loc[common_ids]
    modified_entries = df1_common.compare(df2_common, result_names=("jama", "jira"))

    return new_entries, removed_entries, modified_entries


def export_to_excel(file_name, new_entries, removed_entries, modified_entries):
    """
    Exports the new, removed, and modified entries to an Excel file.
    """
    with pd.ExcelWriter(file_name, engine="xlsxwriter") as writer:
        new_entries.to_excel(writer, sheet_name="New Requirements")
        removed_entries.to_excel(writer, sheet_name="Removed Requirements")
        modified_entries.to_excel(writer, sheet_name="Modified Requirements")

    logging.info("Exported comparison results to %s", file_name)


def synchronize(df1, df2):
    """
    Synchronize two DataFrames and identify new, removed, and modified entries.
    Export the results to an Excel file.
    """
    df1_filtered = df1[["documentKey", "name"]].set_index("documentKey")
    df2_filtered = df2[["documentKey", "name"]].set_index("documentKey")

    # Remove all leading and trailing spaces before comparing data
    df1_filtered = df1_filtered.apply(
        lambda x: x.str.strip() if x.dtype == "object" else x
    )
    df2_filtered = df2_filtered.apply(
        lambda x: x.str.strip() if x.dtype == "object" else x
    )

    # pylint: disable=W0612
    new_entries, removed_entries, modified_entries = compare_dataframes(
        df1_filtered, df2_filtered
    )
    # pylint: enable=W0612

    # export_to_excel(
    #     "src/ska_jama_jira_integration/csv_files/requirements_comparison.xlsx",
    #     new_entries,
    #     removed_entries,
    #     modified_entries,
    # )

    return new_entries


def sync_l1():
    """
    Synchronize Level 1 (L1) requirements between Jira and Jama.
    """
    logging.info("Fetching Jama L1 requirements...")
    jama_l1 = get_jama_requirements("L1", "System")
    jama_l1.to_csv("src/ska_jama_jira_integration/csv_files/jama_l1.csv", index=False)

    logging.info("Fetching Jira L1 requirements...")
    jira_l1 = get_jira_requirements("L1")
    jira_l1.to_csv("src/ska_jama_jira_integration/csv_files/jira_l1.csv", index=False)

    logging.info("Synchronizing L1 requirements...")
    new_entries = synchronize(jira_l1, jama_l1)

    logging.info("Creating jira tickets...")
    # pylint: disable=W0612
    for index, row in new_entries.head(2).iterrows():
        jama_id = index

        # Filter the jama_l1 DataFrame based on the documentKey
        jama_row = jama_l1[jama_l1["documentKey"] == jama_id]
        jama_data = jama_row.iloc[0].to_dict()

        # Create jama url
        jama_url = (
            f"https://skaoffice.jamacloud.com/perspective.req?"
            f"projectId={jama_data['jama_project_id']}&docId={jama_data['id']}"
        )

        requirement = {
            "documentKey": jama_data.get("documentKey"),
            "jama_url": jama_url,
            "name": jama_data.get("name"),
            "description": jama_data.get("description"),
            "status": jama_data.get("status"),
            "verification_method": jama_data.get("verification_method"),
            "verification_milestone": jama_data.get("verification_milestone"),
            "rationale": jama_data.get("rationale"),
            "category": jama_data.get("category"),
            "allocation": jama_data.get("allocation"),
            # "compliance": jama_data.get("compliance"),
            "tags": jama_data.get("tags"),
            "component": [{"name": "System"}],
        }

        create_requirement("L1", requirement)


def sync_l2():
    """
    Synchronize Level 2 (L2) requirements between Jira and Jama for multiple products.
    """

    # Jama L2 Requirements
    l2_products = [
        "TMC",
        "OSO",
        "SDP",
        "PLATFORM",
        "LOW CSP",
        "LOW CBF",
        "LOW PSS",
        "LOW PST",
        "LOW CSP LMC",
        "LOW SPS",
        "LOW ANTENNA ASSEMBLY",
        "MID CSP",
        "MID CSP LMC",
        "MID CBF",
        "MID PST",
        "MID PSS",
        "DSH LMC",
        "DSH ELEMENT",
        "BAND 1",
        "BAND 2",
        "BAND 5",
        "SPF SERVICES",
        "CRYO",
        "LFAA",
        "MCCS",
        "FIELD NODE",
        "LOW NETWORKS",
        "LOW INAU",
        "LOW PASD",
        "SAT",
        "MID INSA",
        "MID NETWORKS",
        "MID SPFRx",
        "DSH STRUCTURE",
        "MID INFRA",
        "MID SAT.STFR.FRQ",
        "MID AA0.5 BAND 5 DOWNCONVERTER",
    ]

    all_dataframes = []

    for product in l2_products:
        logging.info("Fetching Jama L2 requirements for %s...", product)
        jama_df = get_jama_requirements("L2", product)
        jama_df["product"] = product
        all_dataframes.append(jama_df)

    jama_l2 = pd.concat(all_dataframes, ignore_index=True)
    jama_l2.to_csv("src/ska_jama_jira_integration/csv_files/jama_l2.csv", index=False)

    logging.info("Fetching Jira L2 requirements...")
    jira_l2 = get_jira_requirements("L2")
    jira_l2.to_csv("src/ska_jama_jira_integration/csv_files/jira_l2.csv", index=False)

    logging.info("Synchronizing L2 requirements...")
    new_entries = synchronize(jira_l2, jama_l2)

    logging.info("Creating jira tickets...")
    # pylint: disable=W0612
    for index, row in new_entries.head(1).iterrows():
        jama_id = index

        # Filter the jama_l2 DataFrame based on the documentKey
        jama_row = jama_l2[jama_l2["documentKey"] == jama_id]
        jama_data = jama_row.iloc[0].to_dict()

        jama_url = (
            f"https://skaoffice.jamacloud.com/perspective.req?"
            f"projectId={jama_data['jama_project_id']}&docId={jama_data['id']}"
        )

        requirement = {
            "documentKey": jama_data.get("documentKey"),
            "jama_url": jama_url,
            "name": jama_data.get("name"),
            "description": jama_data.get("description"),
            "status": jama_data.get("status"),
            "verification_method": jama_data.get("verification_method"),
            "verification_milestone": jama_data.get("verification_milestone"),
            "rationale": jama_data.get("rationale"),
            "category": jama_data.get("category"),
            "allocation": jama_data.get("allocation"),
            "compliance": jama_data.get("compliance"),
            "tags": jama_data.get("tags"),
            "component": jama_data.get("component"),
        }

        create_requirement("L2", requirement)


def sync_test_cases():
    """
    Synchronize Test Cases between Jira and Jama.
    """
    logging.info("Fetching Jama test cases...")
    jama_test_cases = get_jama_test_cases()
    jama_test_cases.to_csv(
        "src/ska_jama_jira_integration/csv_files/jama_test_cases.csv", index=False
    )

    logging.info("Fetching Jira test cases...")
    jira_test_cases = get_jira_test_cases()
    jira_test_cases.to_csv(
        "src/ska_jama_jira_integration/csv_files/jira_test_cases.csv", index=False
    )

    logging.info("Synchronizing test cases...")
    new_entries = synchronize(jira_test_cases, jama_test_cases)

    logging.info("Creating jira tickets...")
    # pylint: disable=W0612
    for index, row in new_entries.head(1).iterrows():
        jama_id = index

        # Filter the jama_test_cases DataFrame based on the documentKey
        jama_row = jama_test_cases[jama_test_cases["documentKey"] == jama_id]
        jama_data = jama_row.iloc[0].to_dict()

        jama_url = (
            f"https://skaoffice.jamacloud.com/perspective.req?"
            f"projectId={jama_data['jama_project_id']}&docId={jama_data['id']}"
        )

        test_case = {
            "documentKey": jama_data.get("documentKey"),
            "jama_url": jama_url,
            "name": jama_data.get("name"),
            "description": jama_data.get("description"),
            "verification_milestone": jama_data.get("verification_milestone"),
            "test": jama_data.get("test"),
            "status": jama_data.get("status"),
        }

        create_test_case("STC", test_case)


def sync_interfaces():
    """
    Synchronize Interfaces between Jira and Jama.
    """
    logging.info("Fetching Jama interfaces...")
    jama_interfaces = get_jama_interfaces()
    jama_interfaces.to_csv(
        "src/ska_jama_jira_integration/csv_files/jama_interfaces.csv", index=False
    )

    logging.info("Fetching Jira interfaces...")
    jira_interfaces = get_jira_interfaces()
    jira_interfaces.to_csv(
        "src/ska_jama_jira_integration/csv_files/jira_interfaces.csv", index=False
    )

    logging.info("Synchronizing interfaces...")
    new_entries = synchronize(jira_interfaces, jama_interfaces)

    logging.info("Creating jira tickets...")
    # pylint: disable=W0612
    for index, row in new_entries.iterrows():
        jama_id = index

        # Filter the jama_interfaces DataFrame based on the documentKey
        jama_row = jama_interfaces[jama_interfaces["documentKey"] == jama_id]
        jama_data = jama_row.iloc[0].to_dict()

        jama_url = (
            f"https://skaoffice.jamacloud.com/perspective.req?"
            f"projectId={jama_data['jama_project_id']}&docId={jama_data['id']}"
        )

        interface = {
            "documentKey": jama_data.get("documentKey"),
            "jama_url": jama_url,
            "name": jama_data.get("name"),
            "description": jama_data.get("description"),
            "design_compliance": jama_data.get("design_compliance"),
            "status": jama_data.get("status"),
        }

        jira_interface = create_interface("ICD", interface)

        logging.info("Updating Jama item...")
        print(jira_interface["self"])
        # update_jama_item(
        #     1169665,
        #     "https://jira-test-3.skatelescope.org/projects/STC/issues/STC-2062",
        # )
