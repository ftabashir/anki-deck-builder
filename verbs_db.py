import sqlite3

from pydantic import BaseModel

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
    results = search_verb(conn, infinitive)
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
    main()
