import json
import os
import sqlite3

from pydantic import BaseModel

from apkg_from_word_list import read_words
from file_utils import safe_filename

DB_FILE = "./data/verbs.db"


class Verb(BaseModel):
    Infinitive: str
    Präsens_ich: str
    Präsens_du: str
    Präsens_er_sie_es: str
    Präteritum_ich: str
    Partizip_II: str
    Konjunktiv_II_ich: str
    Imperativ_Singular: str
    Imperativ_Plural: str
    Hilfsverb: str


def connect_db():
    return sqlite3.connect(DB_FILE)


def _search_verb(conn, infinitive):
    cursor = conn.cursor()
    query = """
        SELECT Infinitive, Präsens_ich, Präsens_du, "Präsens_er, sie, es",
               Präteritum_ich, `Partizip II`, `Konjunktiv II_ich`,
               `Imperativ Singular`, `Imperativ Plural`, Hilfsverb
        FROM verbs
        WHERE Infinitive LIKE ?
    """
    cursor.execute(query, (f"%{infinitive}%",))
    results = cursor.fetchall()
    return results


def search_verb(conn, infinitive):
    results = _search_verb(conn, infinitive)
    verbs = [
        Verb(
            Infinitive=r[0],
            Präsens_ich=r[1],
            Präsens_du=r[2],
            Präsens_er_sie_es=r[3],
            Präteritum_ich=r[4],
            Partizip_II=r[5],
            Konjunktiv_II_ich=r[6],
            Imperativ_Singular=r[7],
            Imperativ_Plural=r[8],
            Hilfsverb=r[9]
        ) for r in results
    ]
    return verbs


def print_results(results):
    if not results:
        print("No verb found.")
        return

    print(f"{len(results)} results found.")

    for row in results:
        print(f"""
Infinitive:             {row[0]}
Präsens (ich):          {row[1]}
Präsens (du):           {row[2]}
Präsens (er/sie/es):    {row[3]}
Präteritum (ich):       {row[4]}
Partizip II:            {row[5]}
Konjunktiv II (ich):    {row[6]}
Imperativ Singular:     {row[7]}
Imperativ Plural:       {row[8]}
Hilfsverb:              {row[9]}
""")


def main():
    conn = connect_db()
    try:
        while True:
            infinitive = input("🔍 Enter a verb (infinitive or part of it, or 'exit' to quit): ").strip()
            if infinitive.lower() == "exit":
                break
            results = _search_verb(conn, infinitive)
            print_results(results)
    finally:
        conn.close()


if __name__ == "__main__":
    conn = connect_db()

    kapitel = 7
    file_path = f"./data/b2_kontext_kapitel_{kapitel}.txt"
    jsons_directory = f"./data/b2_kontext_kapitel_{kapitel}_jsons_openai"
    words = read_words(file_path)

    for index, word in enumerate(words):
        word_query = word.split(',')[0]
        word_query = word_query.split(' (')[0]
        word_query = word_query.replace('|', '')
        word_query = word_query.strip()

        # if index > 500:
        #     break

        file_path = f'{jsons_directory}/{safe_filename(word_query)}.json'
        if os.path.exists(file_path):
            with open(file_path, 'r', encoding='utf-8') as f:
                word_data = json.load(f)
                if word_data['is_verb']:
                    perfekt_präteritum = word_data['perfekt_präteritum'].split('/')
                    infinitive = word_data['word_query']
                    verb_matches = search_verb(conn, infinitive)
                    exact_match = [verb for verb in verb_matches if verb.Infinitive == infinitive]
                    if len(verb_matches) > 0:
                        print("-" * 20)
                        print(f"{len(verb_matches)} matches for {infinitive}, {len(exact_match)} exact matches")
                        if len(exact_match) == 1:
                            verb_matches = exact_match
                            print('Only exact match is printed.')
                        for verb in verb_matches:
                            print("-" * 20)
                            print("[Infinitive]")
                            print(verb.Infinitive)
                            print("[Präteritum]")
                            print(verb.Präteritum_ich)
                            print(perfekt_präteritum[1].strip())
                            print("[Perfekt]")
                            print(f"{verb.Hilfsverb} {verb.Partizip_II}")
                            print(perfekt_präteritum[0].strip())
                            print()
                    else:
                        print(f"No match for {infinitive}")
