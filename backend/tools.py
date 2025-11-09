import re
import requests
from bs4 import BeautifulSoup
from crewai.tools import tool
import os
from dotenv import load_dotenv
load_dotenv()

SYMPTOM_BASE_URL = os.getenv("SYMPTOM_BASE_URL")

@tool("Symptom Scraper Tool")
def symptom_scraper_tool(symptom_slug: str) -> str:
    """
    Scrapes the MedlinePlus page for the given symptom and returns
    the concatenated text from all paragraph and list elements.
    
    Args:
        symptom_slug (str): Symptom name or slug (e.g., 'headache')
    
    Returns:
        str: Text content of the symptom page
    """
    url = SYMPTOM_BASE_URL + re.sub(r"\s+", "", symptom_slug.lower()) + ".html"
    resp = requests.get(url, timeout=10)
    if resp.status_code != 200:
        return f"Error fetching {url}: {resp.status_code}"
    soup = BeautifulSoup(resp.text, "html.parser")
    elems = soup.find_all(["p", "li"])
    return "\n".join(e.get_text(strip=True) for e in elems if e.get_text(strip=True))
