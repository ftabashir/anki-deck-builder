import time
import os
import json
import genanki
from pydantic import BaseModel

import apkg_collections
from apkg_audio import add_audio
from apkg import print_field_names, get_cursor, search_notes_for_word, get_field_names, get_notes
from file_utils import safe_filename
from format_duration import format_duration
from ollama_api import call_ollama
from openai_api import call_openai

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
    'de_synonyms': 'German synonyms for "{}", comma-separated, max three synonyms, no explanation.',
    # 'fa_meaning': ('معنی کلمه "{}" در زبان فارسی چیست؟ '
    #                'اگر چندین معنی دارد، حداکثر سه تا از متداول ترین ها را ذکر کن. '
    #                'در یک جمله پاسخ بده و معانی مختلف را با "/" جدا کن و توضیح اضافی نده.'
    #                ),
    'fa_meaning': ('Translate the German word "{}" into Persian. '
                   'If it has multiple meanings, give the most common ones. '
                   'Keep the answer in a single line, separate different meanings with /.'
                   ),
    'de_example_sentence': ('Give two example sentences using the German word "{}". '
                            'Each sentence on its own line. Use simple and correct German.'
                            'Do not add any explanations or translations.'
                            ),
    'perfekt_präteritum': ('If "{}" is a German verb, reply with its Perfekt and Präteritum forms, '
                           'separated by a slash. Also include whether the auxiliary verb is "haben" or "sein" for the Perfekt form.\n'
                           'Format: [auxiliary] + [Perfekt] / [Präteritum] \n'
                           'Example: sein + geblieben / blieb \n'
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


class ApkgParams(BaseModel):
    deck_name: str
    deck_id: int
    model_name: str
    model_id: int


def record_time(key, value):
    if key in _times:
        _times[key] += value
    else:
        _times[key] = value


def all_words(collection):
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

def create_json_files(words, jsons_directory):
    _times.clear()
    count = 0
    for index, word in enumerate(words):
        word_query = word.split(',')[0]
        word_query = word_query.split(' (')[0]
        word_query = word_query.replace('|', '')
        word_query = word_query.strip()

        file_path = f'{jsons_directory}/{safe_filename(word_query)}.json'
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


def update_json_files(words, jsons_directory):
    _times.clear()
    count = 0
    for index, word in enumerate(words):
        word_query = word.split(',')[0]
        word_query = word_query.split(' (')[0]
        word_query = word_query.replace('|', '')
        word_query = word_query.strip()

        file_path = f'{jsons_directory}/{safe_filename(word_query)}.json'
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


def create_json_files_with_openai(words, jsons_directory):
    _times.clear()
    count = 0
    for index, word in enumerate(words):
        word_query = word.split(',')[0]
        word_query = word_query.split(' (')[0]
        word_query = word_query.replace('|', '')
        word_query = word_query.strip()

        file_path = f'{jsons_directory}/{safe_filename(word_query)}.json'
        if os.path.exists(file_path):
            print(f'{word_query} already exist')
            continue

        start = time.time()
        (word_data, json_result) = call_openai(word, word_query)
        end = time.time()
        record_time('all_openai', end - start)
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
        for key, time_elapsed in _times.items():
            percentage = round((time_elapsed / total) * 100, 1)
            print(f"{key:<20} {round(time_elapsed, 0):<5} {percentage:<4}% {'=' * int(percentage / 5)}")
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
                <ul style="margin-top: 0px;">
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
                <div><b>🇮🇷 Bedeutung (FA)</b> <br/> {{fa_meaning}}</div><br/>
                <div><b>🔁 Synonyme</b> <br/> {{de_synonyms}}</div><br/>
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
                .small-audio .replay-button {
                  transform: scale(0.5);
                }
                .hidden-audio .replay-button {
                  display: none;
                }
            """


def b2_kontext_fields():
    return [
        {'name': 'word_query'},
        {'name': 'word_query_expanded'},
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


def b2_kontext_fields_data(word_query, word_query_expanded, word, de_meaning, de_meaning_fa, de_synonyms, de_example_1, de_example_fa_1,
                           de_example_2, de_example_fa_2, fa_meaning, en_meaning, part_of_speech, frequency_de,
                           frequency_emoji, cefr_level, perfekt_präteritum, is_verb, color_class):
    return [
        word_query,
        word_query_expanded,
        word,
        de_meaning,
        de_meaning_fa,
        de_synonyms,
        de_example_1,
        de_example_fa_1,
        de_example_2,
        de_example_fa_2,
        fa_meaning,
        en_meaning,
        part_of_speech,
        frequency_de,
        frequency_emoji,
        cefr_level,
        perfekt_präteritum,
        is_verb,
        color_class,
    ]


def create_anki_model(apkg_params: ApkgParams):
    return genanki.Model(
        model_id=apkg_params.model_id,
        name=apkg_params.model_name,
        fields=b2_kontext_fields(),
        templates=[card_template()],
        css=template_css(),
    )


def gen_anki(apkg_params: ApkgParams, jsons_directory, apkg_path):
    my_model = create_anki_model(apkg_params)
    deck = genanki.Deck(
        deck_id=apkg_params.deck_id,
        name=apkg_params.deck_name,
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

                is_verb = "Verb" in data.get("part_of_speech", "")

                word = data.get("word", "")
                part_of_speech = data.get("part_of_speech", "")

                frequency = data.get('frequency', '')
                frequency_de = frequency_map.get(frequency, '')
                frequency_emoji = frequency_emoji_map.get(frequency, '')

                color_class = "black"
                if part_of_speech.lower() == "noun":
                    word_lower = word.lower()
                    if ' der' in word_lower or word_lower.startswith('der '):
                        color_class = "blue"
                    elif ' die' in word_lower or word_lower.startswith('die '):
                        color_class = "red"
                    elif ' das' in word_lower or word_lower.startswith('das '):
                        color_class = "green"

                fields = b2_kontext_fields_data(
                    word_query=data.get('word_query', ''),
                    word_query_expanded=data.get('word_query_expanded', ''),
                    word=data.get('word', ''),
                    de_meaning=data.get('de_meaning', ''),
                    de_meaning_fa=data.get('de_meaning_fa', ''),
                    de_synonyms=' / '.join(data.get('de_synonyms', '')) ,
                    de_example_1=data.get("de_example_1", ""),
                    de_example_fa_1=data.get("de_example_fa_1", ""),
                    de_example_2=data.get("de_example_2", ""),
                    de_example_fa_2=data.get("de_example_fa_2", ""),
                    fa_meaning=data.get('fa_meaning', ''),
                    en_meaning=data.get('en_meaning', ''),
                    part_of_speech=data.get('part_of_speech', ''),
                    frequency_de=frequency_de,
                    frequency_emoji=frequency_emoji,
                    cefr_level=data.get('cefr_level', ''),
                    perfekt_präteritum=data.get('perfekt_präteritum', ''),
                    is_verb="yes" if is_verb else "",
                    color_class=color_class,
                )

                note = genanki.Note(model=my_model, fields=fields)
                deck.add_note(note)

    # Package the deck
    genanki.Package(deck).write_to_file(apkg_path)
    print(f"✅ Done! Your deck is saved as: {apkg_path}")


def find_redundant_words(collection):
    words = all_words(collection)
    word_map = {}
    for word in words:
        word_query = word.split(',')[0]
        word_query = word_query.split(' (')[0]
        word_query = word_query.replace('|', '')
        word_query = word_query.strip()
        if word_query in word_map:
            word_map[word_query].append(word)
        else:
            word_map[word_query] = [word]
    for word_query, words in word_map.items():
        if len(words) == 1:
            continue
        else:
            print('\n', word_query)
            for word in words:
                print('- ', word)


def b2_apkg_params():
    return ApkgParams(
        model_name=f'B2 mit präpositionen',
        model_id=1717600100,
        deck_name=f'B2 mit präpositionen Deck',
        deck_id=2169600500,
    )


if __name__ == '__main__':
    collection = apkg_collections.B2_mitpräpositionen
    jsons_directory = './data/mitpräpositionen'
    apkg_path = f'{collection.collection_path}.apkg'
    # words = all_words(collection)
    # create_json_files(words, jsons_directory)
    # update_json_files(words, jsons_directory)
    apkg_params = b2_apkg_params()
    gen_anki(apkg_params, jsons_directory, apkg_path)

    # b2_kontext = create_anki_model(apkg_params)
    # add_audio(
    #     collection=collection,
    #     model_id=b2_kontext.model_id + 1,
    #     model_name=b2_kontext.name + "|Audio",
    #     old_model_fields=b2_kontext.fields,
    #     old_card_template=b2_kontext.templates[0],
    #     old_card_css=b2_kontext.css,
    #     deck_id=apkg_params.deck_id + 1,
    #     deck_name=f'{apkg_params.deck_name} with Audio',
    #     with_lib='coqui', # piper or coqui
    # )
