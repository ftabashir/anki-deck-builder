import os
from pathlib import Path

from apkg_b2_kontext import create_json_files, update_json_files, gen_anki, ApkgParams, create_json_files_with_openai
from file_utils import safe_filename


def read_words(file_path):
    with open(file_path, "r", encoding="utf-8") as f:
        lines = f.readlines()

    # Strip whitespace and filter out empty lines
    words = [line.strip() for line in lines if line.strip()]
    return words


def find_duplicates():
    file_path = f"./data/b1_plus.txt"
    jsons_directory = f"./data/b1_plus_jsons"
    words = read_words(file_path)
    counts = {}
    for index, word in enumerate(words):
        word_query = word.split(',')[0]
        word_query = word_query.split(' (')[0]
        word_query = word_query.replace('|', '')
        word_query = word_query.strip()
        key = safe_filename(word_query)
        queries = counts.get(key, list())
        queries.append(word)
        counts[key] = queries

    count_duplicates = 0
    for key, queries in counts.items():
        if len(queries) != 1:
            print(f'{key} has {len(queries)} queries')
            for query in queries:
                print(query)
            print()
            count_duplicates += 1

    print(f'{count_duplicates} duplicates found.\n\n')


if __name__ == '__main__':
    # kapitel = 12
    file_path = f"./data/b1_plus.txt"
    apkg_path = f"./data/collections/b1_plus.apkg"
    jsons_directory = f"./data/b1_plus_jsons"
    Path(jsons_directory).mkdir(parents=True, exist_ok=True)
    words = read_words(file_path)
    # create_json_files(words, jsons_directory)
    # update_json_files(words, jsons_directory)
    create_json_files_with_openai(words, jsons_directory)

    apkg_params = ApkgParams(
        model_name=f'B1+ Kontext',
        model_id=1707400100,
        deck_name=f'B1+ Kontext Deck (OpenAI)',
        deck_id=2159500500,
    )
    gen_anki(apkg_params, jsons_directory, apkg_path)
