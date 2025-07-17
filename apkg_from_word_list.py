import os

from apkg_b2_kontext import create_json_files, update_json_files, gen_anki, ApkgParams, create_json_files_with_openai


def read_words(file_path):
    with open(file_path, "r", encoding="utf-8") as f:
        lines = f.readlines()

    # Strip whitespace and filter out empty lines
    words = [line.strip() for line in lines if line.strip()]
    return words


if __name__ == '__main__':
    kapitel = 7
    file_path = f"./data/b2_kontext_kapitel_{kapitel}.txt"
    apkg_path = f"./data/b2_kontext_kapitel_{kapitel}_openai.apkg"
    jsons_directory = f"./data/b2_kontext_kapitel_{kapitel}_jsons_openai"
    os.makedirs(os.path.dirname(jsons_directory), exist_ok=True)
    words = read_words(file_path)
    # create_json_files(words, jsons_directory)
    # update_json_files(words, jsons_directory)
    # create_json_files_with_openai(words, jsons_directory)

    apkg_params = ApkgParams(
        model_name=f'B2 Kontext K_{kapitel:02d}',
        model_id=1707392100 + kapitel,
        deck_name=f'B2 Kontext K_{kapitel:02d} Deck (OpenAI)',
        deck_id=2159400500 + kapitel,
    )
    gen_anki(apkg_params, jsons_directory, apkg_path)
