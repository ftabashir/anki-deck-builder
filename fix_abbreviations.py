import os
import json
import re
import sys

KNOWN_ABBREVIATIONS = {
    "etw.": "etwas",
    "jmd.": "jemand",
    "jdm.": "jemandem",
    "jdn.": "jemanden",
}

# Regex: detect abbreviations like "etw. ", "jmd. " (letters + dot + space)
abbr_pattern = re.compile(r'\b[A-Za-zÄÖÜäöüß]+\.\s')


def find_all_abbreviations(directory):
    """Read JSON files and collect all abbreviations from 'word_query'."""
    all_abbreviations = set()

    for filename in os.listdir(directory):
        if filename.endswith(".json"):
            filepath = os.path.join(directory, filename)

            try:
                with open(filepath, "r", encoding="utf-8") as f:
                    data = json.load(f)
            except json.JSONDecodeError:
                print(f"Skipping {filename}: invalid JSON")
                continue

            if "word_query" in data:
                found = set(abbr_pattern.findall(data["word_query"]))
                all_abbreviations.update(found)
    return all_abbreviations


def expand_abbreviations(text):
    """Replace known abbreviations in a given text."""
    for abbr, full in KNOWN_ABBREVIATIONS.items():
        text = text.replace(abbr, full)
    return text


def process_json_files(directory):
    """Read all JSON files in a directory and expand 'word_query' if needed."""
    for filename in os.listdir(directory):
        if filename.endswith(".json"):
            filepath = os.path.join(directory, filename)

            with open(filepath, "r", encoding="utf-8") as f:
                try:
                    data = json.load(f)
                except json.JSONDecodeError:
                    print(f"Skipping {filename}: invalid JSON")
                    continue

            # Check and expand word_query
            if "word_query" in data:
                expanded = expand_abbreviations(data["word_query"])
                data["word_query_expanded"] = expanded

                # Write back to file
                with open(filepath, "w", encoding="utf-8") as f:
                    json.dump(data, f, ensure_ascii=False, indent=4)
                print(f"Processed {filename}")


if __name__ == "__main__":
    directory = "./data/b2_jsons"
    all_abbreviations = find_all_abbreviations(directory)
    unknown_abbreviation = False
    for abbr in sorted(all_abbreviations):
        if abbr.strip() not in KNOWN_ABBREVIATIONS:
            print(f"Add {abbr} to KNOWN_ABBREVIATIONS otherwise it will be skipped")
            unknown_abbreviation = True
    # if unknown_abbreviation:
        # sys.exit(1)

    process_json_files(directory)
