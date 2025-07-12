import random
import time
import os
import json

import genanki

import apkg_collections
from apkg import print_field_names, get_cursor, search_notes_for_word, get_field_names, get_notes
from ollama import call_ollama

jsons_directory = './data/b2_kontext_jsons'

PROMPTS = {
    'en_meaning': ('Translate the meaning of the German word "{}" into simple English. '
                   'If it has multiple meanings, give the most common ones. '
                   'Keep the answer in a single line, separate different meanings with / and only lower case letters'
                   ),
    'frequency': ('What is the frequency of usage for the German word "{}". '
                  'Respond with one these without any extra explanation: Extremely rare, Uncommon, Fairly common, Very common, Extremely common'
                  ),
    'cefr_level': ('What is the CEFR level of the German word "{}". '
                   'Respond with one these without any extra explanation: A1, A2, B1, B2, C1, C2'
                   ),
    'part_of_speech': 'What part of speech is the German word "{}"? Just say noun, verb, adjective, etc. without extra explanation.',
    'de_meaning': 'Erkläre das deutsche Wort "{}" in einfachem Deutsch, in einem Satz, ohne weitere Erklärungen.',
    'de_synonyms': 'German synonyms for "{}", comma-separated, no explanation.',
    # 'fa_meaning': ('معنی کلمه "{}" در زبان فارسی چیست؟ '
    #                'اگر چندین معنی دارد، حداکثر سه تا از متداول ترین ها را ذکر کن. '
    #                'در یک جمله پاسخ بده و معانی مختلف را با "/" جدا کن و توضیح اضافی نده.'
    #                ),
    'fa_meaning': ('Translate the German word "{}" into Persian. '
                   'If it has multiple meanings, give the most common ones. '
                   'Keep the answer in a single line, separate different meanings with /.'
                   ),
    'de_example_sentence': ('Give two example sentences using the German word "{}". '
                            'Each sentence on its own line. Use B1 or B2 level German. No extra explanation.'
                            ),
    'perfekt_präteritum': ('If "{}" is a German verb, reply with its Perfekt and Präteritum forms '
                           'separated by a slash (e.g. "gegangen / ging"). '
                           'If it’s not a verb, reply with nothing.'
                           )

}

FA_TRANSLATE_SENTENCE_PROMPT = {
    'de_example_sentence_fa': 'Translate these German sentences into Persian without extra explanation: "{}"',
}

FA_TRANSLATE_MEANING_PROMPT = {
    'de_meaning_fa': 'Translate this German text into Persian without extra explanation and do not bring original text in the output: "{}"'
}

_times = {}


def record_time(key, value):
    if key in _times:
        _times[key] += value
    else:
        _times[key] = value


def all_words():
    collection = apkg_collections.B2_Kontext
    cur = get_cursor(collection.collection_path)
    word_index = get_field_names(cur).index("German")
    notes = get_notes(cur)
    words = [fields[word_index] for note_id, fields in notes.items()]
    return words


def print_matches():
    collection = apkg_collections.B2_Kontext
    cur = get_cursor(collection.collection_path)
    print_field_names(cur)
    results = search_notes_for_word(cur, "arbeit")
    for note_id, fields in results:
        print(f"Note ID: {note_id}")
        for i, field in enumerate(fields):
            print(f"  Field {i + 1}: {field}")
        print("-" * 30)


def run_prompt(prompt_key, prompt, word):
    start = time.time()
    response = call_ollama(prompt=prompt.format(word))
    end = time.time()
    record_time(prompt_key, end - start)
    return response


def run_prompts(prompts, word):
    result = {}
    for prompt_key, prompt in prompts.items():
        result[prompt_key] = run_prompt(prompt_key, prompt, word)
    return result


def format_duration(seconds: int):
    days, seconds = divmod(seconds, 86400)  # 86400 = 60 * 60 * 24
    hours, seconds = divmod(seconds, 3600)  # 3600 = 60 * 60
    minutes, seconds = divmod(seconds, 60)
    d, h, m, s = int(days), int(hours), int(minutes), int(seconds)
    return f"{'' if d == 0 else f'{d}d '}{'' if h == 0 else f'{h}h '}{'' if m == 0 else f'{m}m '}{s}s"


def create_json_files():
    words = all_words()
    _times.clear()
    count = 0
    for index, word in enumerate(words):
        word_query = word.split(',')[0]
        word_query = word_query.split(' (')[0]
        word_query = word_query.replace('|', '')
        word_query = word_query.strip()

        file_path = f'{jsons_directory}/{word_query}.json'
        if os.path.exists(file_path):
            print(f'{word_query} already exist')
            continue

        word_data = run_prompts(PROMPTS, word_query)
        word_data['word'] = word
        word_data['word_query'] = word_query

        print(json.dumps(word_data, indent=4))

        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(word_data, f, indent=4, ensure_ascii=False)

        total = sum(_times.values())
        count += 1
        print('-' * 40)
        print(f'word_query:{word_query}')
        print(f'word: {word}')
        print(f'index {index} of {len(words)}')
        print(f'generated: {count}')
        print(f'skipped: {index + 1 - count}')
        print(f'total time: {format_duration(total)}')
        print(f'words per minute: {round(60 / (total / count), 1)}')
        print(f'estimated remaining time: {format_duration((len(words) - index) * (total / count))}')
        print('-' * 40)
        for key, time in _times.items():
            percentage = round((time / total) * 100, 1)
            print(f"{key:<20} {round(time, 0):<5} {percentage:<4}% {'=' * int(percentage / 5)}")
        print('-' * 40)


def update_json_files():
    words = all_words()
    _times.clear()
    count = 0
    for index, word in enumerate(words):
        word_query = word.split(',')[0]
        word_query = word_query.split(' (')[0]
        word_query = word_query.replace('|', '')
        word_query = word_query.strip()

        file_path = f'{jsons_directory}/{word_query}.json'
        if os.path.exists(file_path):
            with open(file_path, 'r', encoding='utf-8') as f:
                word_data = json.load(f)

                update_data = run_prompts(FA_TRANSLATE_SENTENCE_PROMPT, word_data['de_example_sentence'])
                for key, value in update_data.items():
                    word_data[key] = value

                update_data = run_prompts(FA_TRANSLATE_MEANING_PROMPT, word_data['de_meaning'])
                for key, value in update_data.items():
                    word_data[key] = value

                print(json.dumps(word_data, indent=4))

            with open(file_path, "w", encoding="utf-8") as f:
                json.dump(word_data, f, indent=4, ensure_ascii=False)

        total = sum(_times.values())
        count += 1
        print('-' * 40)
        print(f'word_query:{word_query}')
        print(f'word: {word}')
        print(f'index {index} of {len(words)}')
        print(f'generated: {count}')
        print(f'skipped: {index + 1 - count}')
        print(f'total time: {format_duration(total)}')
        print(f'words per minute: {round(60 / (total / count), 1)}')
        print(f'estimated remaining time: {format_duration((len(words) - index) * (total / count))}')
        print('-' * 40)
        for key, time in _times.items():
            percentage = round((time / total) * 100, 1)
            print(f"{key:<20} {round(time, 0):<5} {percentage:<4}% {'=' * int(percentage / 5)}")
        print('-' * 40)


def card_template():
    return {
        'name': 'Card 1',
        'qfmt': """
                <div style="font-size: 24px; color: {{color_class}};">{{word_query}}</div>
                <div style="color: #999999; font-size: 18px;">{{word}}</div>
            """,
        'afmt': """
                {{FrontSide}}<hr>
                <div><b>🧠 Bedeutung (DE)</b> <br/> {{de_meaning}}
                <div style="color: #999999; font-size: 16px;text-align: right;">{{de_meaning_fa}}</div>
                </div><br/>
                <div><b>💬 Beispiel</b> <br/> 
                <ul style="margin-top: 4px;">
                {{#de_example_sentence_1}}
                <li style="font-size: 16px;">{{de_example_sentence_1}}
                {{#de_example_sentence_fa_1}}
                <br/><div style="color: #999999; font-size: 16px;text-align: right;">{{de_example_sentence_fa_1}}</div>
                {{/de_example_sentence_fa_1}}
                </li>
                {{/de_example_sentence_1}}
                {{#de_example_sentence_2}}
                <li style="margin-top: 8px;font-size: 16px;">{{de_example_sentence_2}}
                {{#de_example_sentence_fa_2}}
                <br/><div style="color: #999999; font-size: 16px;text-align: right;">{{de_example_sentence_fa_2}}</div>
                {{/de_example_sentence_fa_2}}
                </li>
                {{/de_example_sentence_2}}
                </ul>
                </div><br/>
                <div><b>🔁 Synonyme</b> <br/> {{de_synonyms}}</div><br/>
                <div><b>🇮🇷 Bedeutung (FA)</b> <br/> {{fa_meaning}}</div><br/>
                <div><b>🇬🇧 Bedeutung (EN)</b> <br/> {{en_meaning}}</div><br/><br/>
                <div><b>🧩 Wortart:</b> {{part_of_speech}}</div>
                {{#is_verb}}
                  <div><b>📚 Perfekt/Präteritum:</b> {{perfekt_präteritum}}</div>
                {{/is_verb}}
                <div><b>📈 Häufigkeit:</b> {{frequency_emoji}} {{frequency}}</div>
                <div><b>🎯 CEFR-Niveau:</b> {{cefr_level}}</div>
            """,
    }


def template_css():
    return """
                .card {
                    font-family: Arial;
                    font-size: 18px;
                    text-align: left;
                    padding: 20px;
                }
            """


def gen_anki():
    fields = [
        {'name': 'word_query'},
        {'name': 'word'},
        {'name': 'de_meaning'},
        {'name': 'de_meaning_fa'},
        {'name': 'de_synonyms'},
        {'name': 'de_example_sentence_1'},
        {'name': 'de_example_sentence_fa_1'},
        {'name': 'de_example_sentence_2'},
        {'name': 'de_example_sentence_fa_2'},
        {'name': 'fa_meaning'},
        {'name': 'en_meaning'},
        {'name': 'part_of_speech'},
        {'name': 'frequency'},
        {'name': 'frequency_emoji'},
        {'name': 'cefr_level'},
        {'name': 'perfekt_präteritum'},
        {"name": "is_verb"},
        {"name": "color_class"},
    ]

    # Create a unique model ID (random so it's reusable)
    model_id = random.randrange(1 << 30, 1 << 31)
    my_model = genanki.Model(
        model_id,
        'B2 Kontext Words|Meanings|Examples',
        fields=fields,
        templates=[card_template()],
        css=template_css(),
    )

    # Create the deck
    deck = genanki.Deck(
        deck_id=random.randrange(1 << 30, 1 << 31),
        name='B2 Kontext Deck'
    )

    frequency_map = {
        'Extremely rare': '️Extrem selten',
        'Uncommon': 'Selten',
        'Fairly common': 'Ziemlich häufig',
        'Very common': 'Sehr häufig',
        'Extremely common': 'Extrem häufig',
    }
    frequency_emoji_map = {
        'Extremely rare': '☀️️',
        'Uncommon': '🌤️',
        'Fairly common': '⛅',
        'Very common': '🌧️',
        'Extremely common': '⛈️',
    }

    # Load all JSON files
    for filename in os.listdir(jsons_directory):
        if filename.endswith('.json'):
            with open(os.path.join(jsons_directory, filename), 'r', encoding='utf-8') as f:
                data = json.load(f)

                de_examples = data.get("de_example_sentence", "").strip().split("\n")
                de_example_1 = de_examples[0] if len(de_examples) > 0 else ''
                de_example_2 = de_examples[1] if len(de_examples) > 1 else ''

                de_example_sentence_fa = data.get("de_example_sentence_fa", "").strip()
                de_example_sentence_fa = de_example_sentence_fa.replace('\n\n', '\n') # remove duplicate new lines
                de_example_sentence_fa = de_example_sentence_fa.replace('"', '') # remove quotation marks
                de_examples_fa = de_example_sentence_fa.split("\n")
                de_example_fa_1 = de_examples_fa[0] if len(de_examples_fa) > 0 else ''
                de_example_fa_2 = de_examples_fa[1] if len(de_examples_fa) > 1 else ''

                is_verb = "Verb" in data.get("part_of_speech", "")

                word = data.get("word", "")
                part_of_speech = data.get("part_of_speech", "")

                frequency = data.get('frequency', '')
                frequency_de = frequency_map.get(frequency, '')
                frequency_emoji = frequency_emoji_map.get(frequency, '')

                color_class = "black"
                if part_of_speech.lower() == "noun":
                    word_lower = word.lower()
                    if ' der' in word_lower:
                        color_class = "blue"
                    elif ' die' in word_lower:
                        color_class = "red"
                    elif ' das' in word_lower:
                        color_class = "green"

                # Safely get fields
                fields = [
                    data.get('word_query', ''),
                    data.get('word', ''),
                    data.get('de_meaning', ''),
                    data.get('de_meaning_fa', ''),
                    data.get('de_synonyms', ''),
                    de_example_1,
                    de_example_fa_1,
                    de_example_2,
                    de_example_fa_2,
                    data.get('fa_meaning', ''),
                    data.get('en_meaning', ''),
                    data.get('part_of_speech', ''),
                    frequency_de,
                    frequency_emoji,
                    data.get('cefr_level', ''),
                    data.get('perfekt_präteritum', ''),
                    "yes" if is_verb else "",
                    color_class,
                ]

                note = genanki.Note(model=my_model, fields=fields)
                deck.add_note(note)

    # Package the deck
    output_file = os.path.join(jsons_directory, "B2_Kontext_Words.apkg")
    genanki.Package(deck).write_to_file(output_file)
    print(f"✅ Done! Your deck is saved as: {output_file}")


if __name__ == '__main__':
    gen_anki()
    # create_json_files()
    # update_json_files()
    # words = all_words()
    # collection = apkg_collections.A1_B2
    # cur = get_cursor(collection.collection_path)
    # word_index = get_field_names(cur).index("Word")
    # found = 0
    # notFound = 0
    # for index, word in enumerate(words):
    #     word_query = word.split(',')[0]
    #     word_query = word_query.split(' (')[0]
    #     word_query = word_query.replace('|', '')
    #     word_query = word_query.strip()
    # results = search_notes_for_word(cur, word_query)
    # word_found = len(results) > 0
    # meaning = ''
    # if not word_found:
    #     meaning = get_meaning(word_query)
    # print(index, word, "-->", word_query,
    #       f"{len(results)} found" if word_found else f"NOT_FOUND meaning= {meaning}")
    # if word_found:
    #     found += 1
    # else:
    #     notFound += 1
    # print(f"Found: {found} NotFound: {notFound}")
