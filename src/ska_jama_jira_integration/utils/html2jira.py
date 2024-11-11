"""
This module provides various utility functions to process HTML content.
"""

import re

from bs4 import BeautifulSoup


def convert_to_jira_wiki(html: str) -> str:
    """
    Parse HTML content to extract text if valid.
    """
    if html and "<" in html:
        soup = BeautifulSoup(html, "html.parser")

        # Handle bold and italic text
        handle_format(soup)

        # Handle hyperlinks
        handle_hyperlinks(soup)

        # Replace <p> and <br> tags with newlines
        handle_new_lines(soup)

        # Handle lists
        all_lists = soup.find_all(["ul", "ol"])
        for lst in all_lists[::-1]:
            if lst.parent:
                list_items = handle_lists(lst)
                list_text = "\n".join(list_items) + "\n\n"
                lst.replace_with(list_text)
            else:
                continue

        # Handle tables
        handle_tables(soup)

        # Get text
        # jira_wiki = str(soup)
        jira_wiki = soup.get_text()

        # Clean up multiple newlines and spaces
        jira_wiki = re.sub(r"\n\s*\n", "\n\n", jira_wiki)
        jira_wiki = re.sub(r"[ \t]+", " ", jira_wiki)

        return jira_wiki.strip()
    return html


def handle_new_lines(soup):
    """
    Processes a BeautifulSoup object by handling new lines for <p> and <br> tags.

    - Inserts double newline characters ("\n\n") after each <p> tag and removes the tag.
    - Replaces each <br> tag with a newline character ("\n").

    Args:
        soup (BeautifulSoup): The BeautifulSoup object containing the HTML content to be
        modified.

    Returns:
        None: Modifies the soup object in place.
    """
    for p in soup.find_all("p"):
        p.insert_after("\n\n")
        p.unwrap()

    for br in soup.find_all("br"):
        br.replace_with("\n")


def handle_format(soup):
    """
    Formats <strong> and <b> tags in a BeautifulSoup object by adding asterisks around
    their text.

    This function finds all <strong> and <b> tags in the provided BeautifulSoup object,
    wraps their text content with asterisks (*), and replaces the original content with
    the formatted string.

    Args:
        soup (BeautifulSoup): The BeautifulSoup object containing the HTML content to be
        modified.

    Returns:
        None: Modifies the soup object in place.
    """
    for strong in soup.find_all(["strong", "b"]):
        strong.string = "*" + strong.get_text() + "*"


def handle_hyperlinks(soup):
    """
    Formats <a> tags in a BeautifulSoup object by replacing them with a markdown-style
    hyperlink.

    This function iterates through all <a> tags in the provided BeautifulSoup object and
    replaces them with a formatted string in the format of '[text | href]'. If the <a>
    tag does not have an 'href' attribute, it replaces the tag with its text content
    only.

    Args:
        soup (BeautifulSoup): The BeautifulSoup object containing the HTML content to be
        modified.

    Returns:
        None: Modifies the soup object in place.
    """
    for a in soup.find_all("a"):
        href = a.get("href", "")
        text = a.get_text()
        if href:
            a.replace_with(f"[{text} | {href}]")
        else:
            a.replace_with(text)


def handle_tables(soup):
    """
    Converts <table> elements in a BeautifulSoup object into Jira table format.

    This function finds all <table> elements in the provided BeautifulSoup object and
    constructs a Jira-formatted table string for each. Each row in the table is
    converted to a line in the format: '| cell1 | cell2 | ... |'. Header cells (<th>)
    and regular cells (<td>) are treated the same, with leading and trailing spaces
    around cell content.

    Args:
        soup (BeautifulSoup): The BeautifulSoup object containing the HTML content to be
        modified.

    Returns:
        None: Prints the Jira-formatted table string for each table found in the soup.
    """
    tables = soup.find_all("table")
    for table in tables:
        jira_table = ""
        rows = table.find_all("tr")
        for row in rows:
            cells = row.find_all(["th", "td"])
            cell_texts = [" " + cell.get_text(strip=True) + " " for cell in cells]
            jira_table += "|" + "|".join(cell_texts) + "|\n"


def handle_lists(tag, indent=""):
    """
    Converts <ul> and <ol> HTML elements into a formatted list representation.

    This function iterates through all <li> tags within the given <ul> or <ol> tag,
    converts them to a string prefixed by a bullet ("*") for unordered lists or a number
    sign ("#") for ordered lists, and handles nested lists recursively with increased
    indentation.

    Args:
        tag (Tag): A BeautifulSoup Tag object representing an HTML <ul> or <ol> element.
        indent (str): A string to prefix each list item for indentation and nested
        structure.

    Returns:
        list: A list of strings where each string represents a line in the formatted
        list.
    """
    bullet = "*" if tag.name == "ul" else "#"
    items = []

    for li in tag.find_all("li", recursive=False):
        line = indent + bullet + " " + li.get_text()
        # Check for nested lists
        for child in li.find_all(["ul", "ol"], recursive=False):
            nested_items = handle_lists(child, indent + bullet)
            line += "\n" + "\n".join(nested_items)
            child.decompose()
        items.append(line)
        li.decompose()
    return items
