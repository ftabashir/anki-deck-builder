import json
import random
import time

from ollama import chat
from pydantic import BaseModel

import apkg_collections
from apkg_b2_kontext import all_words
from format_duration import format_duration


class WordLookupResult(BaseModel):
    de_meaning: str
    en_meaning: str
    fa_meaning: str
    de_synonyms: str
    de_example_sentence_1: str
    de_example_sentence_1_fa_meaning: str
    de_example_sentence_2: str
    de_example_sentence_2_fa_meaning: str
    frequency: str
    cefr_level: str
    part_of_speech: str
    perfekt_präteritum: str


def generate_comparison_table(data):
    html = "<html><head><meta charset='utf-8'><style>table{border-collapse:collapse;}td,th{border:1px solid #ccc;padding:8px;}</style></head><body>"

    keys = list(data[0][0].keys())
    word_key = 'word_query'
    model_key = 'model'
    keys.remove(word_key)
    keys.remove(model_key)
    keys.remove('word')
    keys.remove('time_elapsed')
    keys.insert(0, model_key)

    words = [(word_data[word_key], word_data['word']) for word_data in data[0]]

    for (word_query, word) in words:
        html += f"<h1>{word_query}</h1><table>\n"
        html += f"<h4>{word}</h4><table>\n"

        # collect all keys (for union of fields)
        html += "<tr>"
        for i in range(len(keys)):
            html += f"<th>{keys[i]}</th>"
        html += "</tr>\n"

        word_data = [next((word_data for word_data in model_data if word_data['word_query'] == word_query), None) for
                     model_data in data]
        for obj in word_data:
            html += "<tr>"
            for key in keys:
                html += f"<td>{obj.get(key, 'N/A')}</td>"
            html += "</tr>\n"

        # html += "<tr><td colspan='99' style='background:#eee'></td></tr>"  # row separator

        html += "</table>"

    total_time = format_duration(sum([sum([obj['time_elapsed'] for obj in row]) for row in data]))
    html += f"<h1>Total time: {total_time}</div>"
    html += "</body></html>"
    return html


def get_prompt(word_query):
    return f'What is the JSON result of a dictionary looking up for the word "{word_query}".'


def get_prompt_2(word_query):
    return (f'You are a kind of dictionary which can look up for German words.'
            f'Here we are looking up for the word "{word_query}". '
            f'The output should contain these items:'
            f'- de_meaning: Explain the German word "{word_query}" in simple German, in one sentence, without further explanation.'
            f'- en_meaning: Translate the meaning of the German word "{word_query}" into simple English. If it has multiple meanings, give the most common ones. Keep the answer in a single line, separate different meanings with / and only lower case letters.'
            f'- fa_meaning: Translate the German word "{word_query}" into Persian. If it has multiple meanings, give the most common ones. Keep the answer in a single line, separate different meanings with /.'
            f'- de_synonyms: German synonyms for "{word_query}", comma-separated, no explanation.'
            f'- de_example_sentence_1: Give the first example sentences using the German word "{word_query}". Use B1 or B2 level German. No extra explanation.'
            f'- de_example_sentence_1_fa_meaning: Translate de_example_sentence_1, the first German sentence into Persian without extra explanation.'
            f'- de_example_sentence_2: Give the second example sentences using the German word "{word_query}". Use B1 or B2 level German. No extra explanation.'
            f'- de_example_sentence_2_fa_meaning: Translate de_example_sentence_2, the second German sentence into Persian without extra explanation.'
            f'- frequency: What is the frequency of usage for the German word "{word_query}". Respond with one these without any extra explanation: Extrem selten, Selten, Ziemlich häufig, Sehr häufig, Extrem häufig.'
            f'- cefr_level: What is the CEFR level of the German word "{word_query}". Respond with one these without any extra explanation: A1, A2, B1, B2, C1, C2'
            f'- part_of_speech: What part of speech is the German word "{word_query}"? Just say Substantiv, Verb, Adjektiv, etc. without extra explanation.'
            f'- perfekt_präteritum: If "{word_query}" is a German verb, reply with its Perfekt and Präteritum forms separated by a slash (e.g. "habe gedacht / dachte"). If it’s not a verb, reply with empty string.'
            )


if __name__ == '__main__':
    data = []
    all_words = all_words(apkg_collections.B2_Kontext)
    random.seed(121)
    words = random.sample(all_words, 20)
    models = [
        'gemma3:12b',
        'llama3:8b',
        'phi3:14b', 'phi4:14b',
        'mistral-nemo:12b',
        'deepseek-v2:16b', 'deepseek-llm:7b', 'deepseek-r1:14b',
    ]

    for model in models:
        print(f'--- Model: {model} ---')
        # Warm up message!
        response = chat(
            messages=[{'role': 'user', 'content': 'Hello', }],
            model=model,
            stream=False,
            options={'temperature': 0},
            think=False,
        )
        print(f'warm up response: {response.message.content}')
        model_data = []
        for index, word in enumerate(words):
            word_query = word.split(',')[0]
            word_query = word_query.split(' (')[0]
            word_query = word_query.replace('|', '')
            word_query = word_query.strip()

            start = time.time()
            response = chat(
                messages=[{'role': 'user', 'content': get_prompt(word_query), }],
                model=model,
                stream=False,
                options={'temperature': 0},
                think=False,
                format=WordLookupResult.model_json_schema(),
            )

            wordLookupResult = WordLookupResult.model_validate_json(response.message.content)

            end = time.time()
            time_elapsed = end - start

            print(f'::time:: {int(time_elapsed)}')
            print(json.dumps(wordLookupResult.__dict__, indent=4))
            dict_data = wordLookupResult.__dict__
            dict_data['time_elapsed_int'] = int(time_elapsed)
            dict_data['time_elapsed'] = time_elapsed
            dict_data['model'] = model
            dict_data['word_query'] = word_query
            dict_data['word'] = word
            model_data.append(dict_data)
        data.append(model_data)

        # Generate HTML
        html_content = generate_comparison_table(data)
        # Save to file
        output_path = "comparison_table.html"
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(html_content)

        print(f"HTML saved to {output_path} for {index + 1} words.")
