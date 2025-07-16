import sqlite3
import json

import apkg_collections
from ollama_api import call_ollama


def get_cursor(collection_name, database_name="collection.anki21"):
    # Connect to collection.anki21 or collection.anki2
    conn = sqlite3.connect(collection_name + "_extracted/" + database_name)
    return conn.cursor()


def get_notes(cur):
    # Get the note id and fields (as a string with tab-separated fields)
    cur.execute("SELECT id, flds FROM notes")
    return {note_id: flds.split('\x1f') for note_id, flds in cur.fetchall()}

def search_notes(cur, field_name, word):
    # Get the note id and fields (as a string with tab-separated fields)
    cur.execute("SELECT id, flds FROM notes WHERE flds LIKE ?")
    return {note_id: flds.split('\x1f') for note_id, flds in cur.fetchall()}


def get_cards(cur):
    # Get cards, linked to notes. Get deck ID per card.
    cur.execute("SELECT id, nid, did FROM cards")
    return cur.fetchall()


def get_decks(cur):
    # Load decks from the JSON in col table
    cur.execute("SELECT decks FROM col")
    decks_json = cur.fetchone()[0]
    print(decks_json)
    return json.loads(decks_json)


def get_models(cur):
    # Load models from the JSON in col table
    cur.execute("SELECT models FROM col")
    models_json = cur.fetchone()[0]
    return json.loads(models_json)


def update(field_index, update_func, collection_name, database_name="collection.anki21"):
    """
    Replace a specific field in all notes using a custom function.

    :param collection_name: Path to collection.anki21 (or collection.anki2)
    :param database_name: collection.anki21 (or collection.anki2)
    :param field_index: Index of the field to modify (0 = first field)
    :param update_func: A function that takes the current value and returns the new one
    """
    # Connect to the Anki collection
    conn = sqlite3.connect(collection_name + "/" + database_name)
    cur = conn.cursor()

    # Fetch all notes
    cur.execute("SELECT id, flds FROM notes")
    notes = cur.fetchall()

    # Loop through each note and update the target field
    for note_id, flds in notes:
        fields = flds.split('\x1f')  # Split fields
        if field_index < len(fields):
            old_value = fields[field_index]
            fields[field_index] = update_func(old_value)  # Replace field
            new_flds = '\x1f'.join(fields)
            cur.execute("UPDATE notes SET flds = ? WHERE id = ?", (new_flds, note_id))

    # Save changes
    conn.commit()
    conn.close()


def add_new_field(update_func, collection_name, database_name="collection.anki21"):
    conn = sqlite3.connect(collection_name + "/" + database_name)
    cur = conn.cursor()

    # Step 1: Load note model info
    models = get_models(cur)

    # We'll just use the first model
    model_id, model_data = next(iter(models.items()))

    field_names = [f['name'] for f in model_data['flds']]
    de_word_index = field_names.index("de_word")
    de_sentence_index = field_names.index("de_sentence")
    new_field_name = "fa_word"
    if new_field_name not in field_names:
        # Step 2: Add new field to the model
        model_data['flds'].append({
            "name": new_field_name,
            "media": [],
            "rtl": True,
            "sticky": False,
            "font": "Arial",
            "size": 20,
            "ord": len(model_data['flds'])
        })
        model_data['flds'].append({
            "name": "fa_sentence",
            "media": [],
            "rtl": True,
            "sticky": False,
            "font": "Arial",
            "size": 20,
            "ord": len(model_data['flds'])
        })

        en_word = "en_word"
        for template in model_data['tmpls']:
            for key in ['qfmt', 'afmt']:  # question and answer format
                if en_word in template[key]:
                    new_template_appendix = f"""
                    <br><br>
                    {{{{fa_word}}}}
                    {{{{#fa_sentence}}}}
                    <br><br>
                    <i>{{{{fa_sentence}}}}</i>
                    {{{{/fa_sentence}}}}
                    """.strip()
                    template[key] = template[key] + new_template_appendix
                    # template[key] = template[key].replace(f'{{{{{en_word}}}}}', f'{{{{{new_field_name}}}}}')

        model_data['name'] = model_data['name'] + "_farsi"

        models[model_id] = model_data
        cur.execute("UPDATE col SET models = ?", (json.dumps(models),))

    # Step 3: Process each note
    cur.execute("SELECT id, flds FROM notes")
    notes = cur.fetchall()

    for index, (note_id, flds) in enumerate(notes):
        fields = flds.split('\x1f')
        de_sentence = fields[de_sentence_index]
        old_field = fields[de_word_index]
        print(index, "/", len(notes))
        print("old:", old_field, "sentence:", de_sentence)
        # new_field, new_sentence = ("", "") if index > 20 else update_func(old_field, de_sentence)
        new_field, new_sentence = update_func(old_field, de_sentence)
        print(" new:", new_field, "sentence:", new_sentence)
        fields.append(new_field)
        fields.append(new_sentence)
        new_flds = '\x1f'.join(fields)
        cur.execute("UPDATE notes SET flds = ? WHERE id = ?", (new_flds, note_id))

    conn.commit()
    conn.close()


def get_field_names(cur):
    cur.execute("SELECT models FROM col")
    models = get_models(cur)
    # We'll just use the first model
    model_id, model_data = next(iter(models.items()))
    field_names = [fld['name'] for fld in model_data['flds']]
    return field_names


def search_notes_for_word(cur, search_word):
    # Search notes that contain the word anywhere in any field
    query = "SELECT id, flds FROM notes WHERE flds LIKE ?"
    cur.execute(query, (f'%{search_word}%',))

    results = cur.fetchall()
    return [(note_id, flds.split('\x1f')) for note_id, flds in results]


def print_field_names(cur):
    print(get_field_names(cur))


if __name__ == '__main__':
    collection = apkg_collections.B2_Kontext
    print_field_names(get_cursor(collection.collection_path))
    # update(
    #     field_index=1,
    #     collection_name=collection_name,
    #     update_func=lambda x: x.upper()
    # )

    # add_new_field(
    #     collection_name=collection_name,
    #     update_func=lambda word, sentence: (
    #         call_ollama(
    #             'Translate the german word "' + word + '" to Persian without any extra explanation.' +
    #             'An example usage of this word is: "' + sentence + '"'
    #         ),
    #         call_ollama(
    #             'Translate this german sentence to Persian without any extra explanation: "' + sentence + '"'
    #         )
    #     )
    # )
    # print_field_names(get_cursor(collection_name))
