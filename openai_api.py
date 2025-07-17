import openai
import json

# Set your OpenAI API key
openai.api_key = "your-api-key-here"


def call_openai(word, word_query):
    prompt = f"""
You are a helpful German language assistant.
Provide more details about: "{word_query}". 
Given the German word "{word}", return a JSON object with the following structure:

{{
  "de_meaning": "A simple explanation in simple German of what this word means.",
  "de_meaning_fa": "Persian translation of the German explanation.",
  "de_synonyms": ["synonym1", "synonym2", "synonym3"],
  "de_example_1": "Simple German sentence using the word.",
  "de_example_fa_1": "Persian translation of the first example sentence.",
  "de_example_2": "Another simple German sentence using the word.",
  "de_example_fa_2": "Persian translation of the second example sentence.",
  "fa_meaning": "Persian translation of the actual word meaning.",
  "en_meaning": "English translation of the word meaning.",
  "part_of_speech": "German term for the part of speech (e.g. Verb, Substantiv, Adjektiv, etc).",
  "article": "If noun, include the correct article (der/die/das). Otherwise leave empty.",
  "frequency_de": "How frequent is this word in German? (Extremely rare, Uncommon, Fairly common, Very common, Extremely common)",
  "cefr_level": "CEFR level of the word: A1, A2, B1, B2, C1, or C2",
  "perfekt_präteritum": "If the word is a verb, give the format: [auxiliary] + [Perfekt] / [Präteritum]. Example: sein + geblieben / blieb. If not a verb, leave this empty.",
  "is_verb": true or false
}}

Make sure the JSON is valid.
"""

    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.5
    )

    result = response['choices'][0]['message']['content']

    # Try to parse JSON if possible
    try:
        data = json.loads(result)
        return (data, result)
    except json.JSONDecodeError:
        print("Failed to parse JSON. Response:")
        print(result)
        return None


if __name__ == '__main__':
    # Example usage:
    (word_info, json_result) = call_openai(
        'beziehen von (+ Dat.) (etwas von lokalen Herstellern beziehen)',
        'beziehen von',
    )
    print(json.dumps(word_info, indent=2, ensure_ascii=False))
