import os
import time
import wave
from piper import PiperVoice, SynthesisConfig
import genanki
import apkg_collections
from apkg import get_cursor, get_notes, get_field_names
from extract_apkg import extract_apkg


def new_model(model_id, model_name, old_model_fields, old_card_template):
    fields = [f for f in old_model_fields]
    fields.append({'name': 'word_query_audio'}, )
    card_template = old_card_template.copy()
    word_query_audio = """
                {{#word_query_audio}}
                {{word_query_audio}}
                {{/word_query_audio}}
    """
    card_template['qfmt'] = card_template['qfmt'] + word_query_audio
    templates = [card_template]
    return genanki.Model(
        model_id,
        model_name,
        fields,
        templates,
    )


_syn_config = SynthesisConfig(
    volume=1.0,
    length_scale=1.2,  # 1.2 slower
    noise_scale=1.0,  # more audio variation
    noise_w_scale=1.0,  # more speaking variation
    normalize_audio=False,  # use raw audio from voice
)


def synthesize_wav(text, file_path, model_path='./de_DE-thorsten-high.onnx'):
    voice = PiperVoice.load(model_path)
    os.makedirs(os.path.dirname(file_path), exist_ok=True)
    with wave.open(file_path, "w") as wav_file:
        voice.synthesize_wav(text, wav_file, _syn_config)


def add_audio(collection, model_id, model_name, old_model_fields, old_card_template, deck_id, deck_name):
    apkg_path = f'{collection.collection_path}.apkg'
    new_apkg_path = f'{collection.collection_path}|Audio.apkg'
    extract_to = f'{collection.collection_path}_extracted'
    extract_apkg(apkg_path, extract_to)

    cur = get_cursor(extract_to, collection.database_name)
    field_names = get_field_names(cur)
    cur.execute("SELECT id, guid, flds FROM notes")
    notes_data = cur.fetchall()
    print(len(notes_data))

    model = new_model(
        model_id,
        model_name,
        old_model_fields,
        old_card_template,
    )

    deck = genanki.Deck(deck_id, deck_name)
    package = genanki.Package(deck, media_files=[])

    for i, (note_id, guid, flds) in enumerate(notes_data):
        fields = flds.split('\x1f')  # Fields are separated by unit separator
        field_index = field_names.index('word_query')
        word_query = fields[field_index]
        audio_file_path = f'./audios/{word_query}.wav'
        print(f'Generate audio for index:{i}')
        start = time.time()
        synthesize_wav(word_query, audio_file_path)
        end = time.time()
        print(f'Generate audio for index:{i} finished. time:{end - start}')
        audio_tag = f'[sound:{os.path.basename(audio_file_path)}]'
        new_fields = [f for f in fields]
        new_fields.append(audio_tag)

        new_note = genanki.Note(
            model=model,
            fields=new_fields,
        )
        deck.add_note(new_note)
        package.media_files.append(audio_file_path)

    package.write_to_file(new_apkg_path)
    print(f"✅ Done! Your deck with audios 🔈 is saved as: {new_apkg_path}")
