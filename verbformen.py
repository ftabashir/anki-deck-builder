import requests
from bs4 import BeautifulSoup
import json
import time
import random

from pydantic import BaseModel

from ollama_api import call_ollama


def _beautiful_soup(verb):
    url = f"https://www.verbformen.com/conjugation/{verb}.htm"
    headers = {
        "User-Agent": "Mozilla/5.0"
    }

    # Add delay to avoid getting blocked
    time.sleep(random.uniform(1.5, 3.5))

    res = requests.get(url, headers=headers)
    if res.status_code != 200:
        return {"error": f"Failed to fetch verb: {verb}"}

    return BeautifulSoup(res.text, "html.parser")


def get_verb_forms(verb):
    soup = _beautiful_soup(verb)
    try:
        # Extract the row containing "ich" (1st person singular, Präteritum & Perfekt)
        table = soup.find("table", class_="vTbl")
        rows = table.find_all("tr")

        praeteritum = None
        perfekt = None

        for row in rows:
            cells = row.find_all("td")
            if not cells or len(cells) < 2:
                continue
            label = cells[0].get_text(strip=True)
            form = cells[1].get_text(strip=True)

            if label.startswith("ich") and "Präteritum" in row.get("title", ""):
                praeteritum = form
            elif label.startswith("ich") and "Perfekt" in row.get("title", ""):
                perfekt = form

        return {
            "verb": verb,
            "praeteritum": praeteritum,
            "perfekt": perfekt
        }

    except Exception as e:
        return {"error": str(e)}


class VerbFormLookupResult(BaseModel):
    perfekt: str
    präteritum: str


def get_verb_forms_2(verb):
    print(f'beautiful_soup for verb: {verb}')
    soup = _beautiful_soup(verb)
    text = soup.get_text(separator="\n", strip=True)
    from ollama import chat
    model = 'gemma3:12b'
    print(f'asking ollama model {model}')
    response = chat(
        messages=[{'role': 'user', 'content': f'Extract perfekt and präteritum form of verb from this page: {text}', }],
        model='gemma3:12b',
        stream=False,
        options={'temperature': 0},
        format=VerbFormLookupResult.model_json_schema(),
    )
    return VerbFormLookupResult.model_validate_json(response.message.content)


# Example usage
if __name__ == "__main__":
    verb = "ablaufen"
    result = get_verb_forms_2(verb)
    print(json.dumps(result.__dict__, indent=2, ensure_ascii=False))
