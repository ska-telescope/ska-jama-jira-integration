"""
This module provides various utility functions to interact with YAML-based lookup fields
and process HTML content. It includes functions to retrieve statuses, compliances,
milestones, and allocations from a YAML file, and also to parse and format HTML content
for test cases.
"""

import yaml
from bs4 import BeautifulSoup
import re

# Load the YAML file
with open(
    "src/ska_jama_jira_integration/jama/lookup_fields.yaml", "r", encoding="utf-8"
) as file:
    data = yaml.safe_load(file)


def lookup_status(status_id):
    """
    Looks up a status in the loaded YAML data based on the provided Status ID.
    """
    for status in data["statuses"]:
        if status["Status ID"] == status_id:
            return status["Status"]
    return "Status ID not found"


def lookup_compliances(compliance_id):
    """
    Looks up a compliance in the loaded YAML data based on the provided Compliance ID.
    """
    for status in data["compliances"]:
        if status["Compliance ID"] == compliance_id:
            return status["Compliance"]
    return "Compliance ID not found"


def lookup_milestones(milestone_id):
    """
    Looks up a milestone in the loaded YAML data based on the provided Milestone ID.
    """
    for status in data["milestones"]:
        if status["Milestone ID"] == milestone_id:
            return status["Milestone"]
    return "Milestone ID not found"


def lookup_allocations(allocation_id):
    """
    Looks up an allocation in the loaded YAML data based on the provided Allocation ID.
    """
    for status in data["allocations"]:
        if status["Allocation ID"] == allocation_id:
            return status["Allocation"]
    return "Allocation ID not found"


def get_milestones(milestone_ids):
    """
    Retrieve milestones from IDs.
    """
    if milestone_ids:
        return ",".join(lookup_milestones(m_id) for m_id in milestone_ids)
    return ""


def get_test_case(test_steps):
    """
    Transform test steps into a full test
    """
    result = []

    if test_steps:
        for idx, step in enumerate(test_steps, start=1):
            action = parse_html(step.get("action", ""))
            expected_result = parse_html(step.get("expectedResult", ""))

            step_str = f"Step #{idx} {action}\n"
            step_str += f"Result #{idx} {expected_result}\n"

            result.append(step_str)

    return "----\n".join(result)


def parse_html(html: str) -> str:
    """
    Parse HTML content to extract text if valid.
    """
    if html and "<" in html:
        soup = BeautifulSoup(html, "html.parser")

        # Handle bold and italic text
        for strong in soup.find_all(["strong", "b"]):
            strong.string = "*" + strong.get_text() + "*"

        # Handle hyperlinks
        for a in soup.find_all("a"):
            href = a.get("href", "")
            text = a.get_text()
            # Format as [text](url)
            if href:
                a.replace_with(f"[{text} | {href}]")
            else:
                a.replace_with(text)

        # Replace <p> and <br> tags with newlines
        for p in soup.find_all("p"):
            p.insert_after("\n\n")
            p.unwrap()

        # Handle lists
        def handle_lists(tag, indent=""):
            bullet = "*" if tag.name == "ul" else "#"
            items = []
            for li in tag.find_all("li", recursive=False):
                line = indent + bullet + " " + li.get_text(strip=True)
                # Check for nested lists
                for child in li.find_all(["ul", "ol"], recursive=False):
                    nested_items = handle_lists(child, indent + bullet)
                    line += "\n" + "\n".join(nested_items) + "TEST"
                    child.decompose()
                items.append(line)
                li.decompose()
            return items

        # Process all lists
        all_lists = soup.find_all(["ul", "ol"])
        for lst in all_lists[::-1]:  # Process from innermost to outermost
            if lst.parent:
                list_items = handle_lists(lst)
                list_text = "\n".join(list_items) + "\n\n"
                lst.replace_with(list_text)
            else:
                # If the list has been removed already, skip it
                continue

        # Get text
        jira_wiki = soup.get_text()

        # Clean up multiple newlines and spaces
        jira_wiki = re.sub(r"\n\s*\n", "\n\n", jira_wiki)
        jira_wiki = re.sub(r"[ \t]+", " ", jira_wiki)

        return jira_wiki.strip()
    return html


def parse_html_1(html: str) -> str:
    """
    Transform HTML into JIRA Wiki Markup
    """
    soup = BeautifulSoup(html, "html.parser")

    # # Replace headings
    # for i in range(6, 0, -1):
    #     for header in soup.find_all(f"h{i}"):
    #         header_text = header.get_text()
    #         jira_header = "h" + str(i) + ". " + header_text
    #         header.replace_with(jira_header)

    # Handle bold and italic text
    for strong in soup.find_all(["strong", "b"]):
        strong.string = "*" + strong.get_text() + "*"

    # for em in soup.find_all(["em", "i"]):
    #     em.string = "_" + em.get_text() + "_"

    # # Handle strikethrough text
    # for s in soup.find_all(["s", "strike"]):
    #     s.string = "-" + s.get_text() + "-"

    # # Handle colored text
    # for span in soup.find_all("span"):
    #     style = span.get("style", "")
    #     color_match = re.search("color:\s*(#[0-9a-fA-F]+)", style)
    #     if color_match:
    #         color_code = color_match.group(1)
    #         span.string = "{color:" + color_code + "}" + span.get_text() + "{color}"

    # # Handle lists
    # def handle_lists(tag, indent=""):
    #     bullet = "*" if tag.name == "ul" else "#"
    #     items = []
    #     for li in tag.find_all("li", recursive=False):
    #         line = indent + bullet + " " + li.get_text(strip=True)
    #         # Check for nested lists
    #         for child in li.find_all(["ul", "ol"], recursive=False):
    #             nested_items = handle_lists(child, indent + bullet)
    #             line += "\n" + "\n".join(nested_items)
    #             child.decompose()
    #         items.append(line)
    #         li.decompose()
    #     return items

    # # Process all lists
    # all_lists = soup.find_all(["ul", "ol"])
    # for lst in all_lists[::-1]:  # Process from innermost to outermost
    #     if lst.parent:
    #         list_items = handle_lists(lst)
    #         list_text = "\n".join(list_items) + "\n\n"
    #         lst.replace_with(list_text)
    #     else:
    #         # If the list has been removed already, skip it
    #         continue

    # # Handle tables
    # tables = soup.find_all("table")
    # for table in tables:
    #     jira_table = ""
    #     rows = table.find_all("tr")
    #     for row in rows:
    #         cells = row.find_all(["th", "td"])
    #         cell_texts = [" " + cell.get_text(strip=True) + " " for cell in cells]
    #         jira_table += "|" + "|".join(cell_texts) + "|\n"
    #     table.replace_with(jira_table)

    # Replace <p> and <br> tags with newlines
    for p in soup.find_all("p"):
        p.insert_after("\n\n")
        p.unwrap()

    # for br in soup.find_all("br"):
    #     br.replace_with("\n")

    # # Remove images but keep alt text
    # for img in soup.find_all("img"):
    #     alt_text = img.get("alt", "")
    #     img.replace_with("!" + alt_text + "!")

    # Get text
    jira_wiki = soup.get_text()

    # Clean up multiple newlines and spaces
    jira_wiki = re.sub(r"\n\s*\n", "\n\n", jira_wiki)
    jira_wiki = re.sub(r"[ \t]+", " ", jira_wiki)

    return jira_wiki.strip()
