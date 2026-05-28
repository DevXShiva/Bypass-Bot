import re
from bs4 import BeautifulSoup

def find_links_by_pattern(html: str, pattern: str) -> list:
    """
    Finds all links inside an HTML string matching a specific regex pattern.
    Useful for extracting intermediate or final download URLs.
    """
    return re.findall(pattern, html)

def extract_form_data(html: str) -> dict:
    """
    Extracts all hidden and visible input fields from the first form found in HTML.
    Essential for shorteners that require multi-step form submissions.
    """
    soup = BeautifulSoup(html, "html.parser")
    form = soup.find("form")
    data = {}
    if form:
        for input_tag in form.find_all("input"):
            name = input_tag.get("name")
            if name:
                data[name] = input_tag.get("value", "")
    return data

def get_element_by_text(html: str, tag: str, text_content: str) -> str:
    """
    Finds a specific tag containing certain text and returns its href or value.
    """
    soup = BeautifulSoup(html, "html.parser")
    element = soup.find(tag, string=re.compile(text_content, re.IGNORECASE))
    if element and element.get("href"):
        return element.get("href")
    return ""