"""
Synchronize JIRA and JAMA dataframes
"""

import logging

import pandas as pd

from ska_jama_jira_integration.jama.service import (
    get_jama_requirements,
    get_jama_test_cases,
)
from ska_jama_jira_integration.jira.service import (
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


def sync(df1, df2):
    """
    Synchronize two DataFrames and identify new, removed, and modified entries.
    Export the results to an Excel file.
    """
    df1_filtered = df1[["jama_id", "name", "description"]].set_index("jama_id")
    df2_filtered = df2[["jama_id", "name", "description"]].set_index("jama_id")

    # Remove all leading and trailing spaces before comparing data
    df1_filtered = df1_filtered.apply(
        lambda x: x.str.strip() if x.dtype == "object" else x
    )
    df2_filtered = df2_filtered.apply(
        lambda x: x.str.strip() if x.dtype == "object" else x
    )

    new_entries, removed_entries, modified_entries = compare_dataframes(
        df1_filtered, df2_filtered
    )
    export_to_excel(
        "src/ska_jama_jira_integration/csv_files/requirements_comparison.xlsx",
        new_entries,
        removed_entries,
        modified_entries,
    )

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
    new_entries = sync(jira_l1, jama_l1)
    for index, row in new_entries.head(2).iterrows():
        jama_id = index
        print(jama_id)
        print(row)

    #     # Filter the jama_l1 DataFrame based on the document_key
    #     jama_row = jama_l1[jama_l1["jama_id"] == document_key]

    #     # Accessing the values in the matched row
    #     name = jama_row.iloc[0]["name"]
    #     description = jama_row.iloc[0]["description"]
    #     rationale = jama_row.iloc[0]["rationale"]

    #     # create_requirement("L1", document_key, name, description, rationale)


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
    new_entries = sync(jira_l2, jama_l2)
    for index, row in new_entries.head(2).iterrows():
        jama_id = index
        print(jama_id)
        print(row)
    #     create_requirement("L1", entry)


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
    new_entries = sync(jira_test_cases, jama_test_cases)

    for index, row in new_entries.head(2).iterrows():
        jama_id = index
        print(jama_id)
        print(row)

        # Filter the jama_l1 DataFrame based on the jama_id
        # jama_row = jama_test_cases[jama_test_cases["jama_id"] == jama_id]

        # Accessing the values in the matched row
        # name = jama_row.iloc[0]["name"]
        # description = jama_row.iloc[0]["description"]

        # create_test_case("STC", jama_id, name, description)
