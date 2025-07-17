from apkg_b2_kontext import create_json_files, update_json_files, gen_anki, ApkgParams


def read_words(file_path):
    with open(file_path, "r", encoding="utf-8") as f:
        lines = f.readlines()

    # Strip whitespace and filter out empty lines
    words = [line.strip() for line in lines if line.strip()]
    return words


if __name__ == '__main__':
    file_path = "./data/b2_kontext_kapitel_9.txt"
    jsons_directory = "./data/b2_kontext_kapitel_9_jsons"
    apkg_path = "./data/b2_kontext_kapitel_9.apkg"
    words = read_words(file_path)
    create_json_files(words, jsons_directory)
    update_json_files(words, jsons_directory)

    apkg_params = ApkgParams(
        model_name='B2 Kontext K_09',
        model_id=1607392109,
        deck_name='B2 Kontext K_09 Deck',
        deck_id=2059400509,
    )
    gen_anki(apkg_params, jsons_directory, apkg_path)
