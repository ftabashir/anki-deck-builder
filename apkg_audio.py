import os
import time
import wave
from piper import PiperVoice, SynthesisConfig
import genanki
from apkg import get_cursor, get_field_names
from extract_apkg import extract_apkg
from file_utils import safe_filename
from format_duration import format_duration
from tts_coqui import coqui_generate_audio


def new_model(model_id, model_name, old_model_fields, old_card_template, old_card_css):
    fields = [f for f in old_model_fields]
    fields.append({'name': 'word_query_audio'}, )
    fields.append({'name': 'de_example_sentence_1_audio'}, )
    fields.append({'name': 'de_example_sentence_2_audio'}, )
    fields.append({'name': 'silent_audio'}, )
    card_template = old_card_template.copy()
    word_query_audio = """
                {{#word_query_audio}}
                {{word_query_audio}}
                {{/word_query_audio}}
    """
    de_example_sentence_1_audio = """
                        {{#de_example_sentence_1_audio}}
                        <span class="small-audio">{{de_example_sentence_1_audio}}</span>
                        {{/de_example_sentence_1_audio}}
            """
    de_example_sentence_2_audio = """
                        {{#de_example_sentence_2_audio}}
                        <span class="small-audio">{{de_example_sentence_2_audio}}</span>
                        {{/de_example_sentence_2_audio}}
        """
    silent_audio_template = """<span class="hidden-audio">{{silent_audio}}</span>"""
    card_template['qfmt'] = card_template['qfmt'] + word_query_audio
    card_template['afmt'] = card_template['afmt'].replace('<div><b>💬 Beispiel</b>',
                                                          silent_audio_template + '<div><b>💬 Beispiel</b>')
    card_template['afmt'] = card_template['afmt'].replace('{{de_example_sentence_1}}',
                                                          '{{de_example_sentence_1}}' + de_example_sentence_1_audio)
    card_template['afmt'] = card_template['afmt'].replace('{{de_example_sentence_2}}',
                                                          '{{de_example_sentence_2}}' + de_example_sentence_2_audio)
    templates = [card_template]
    return genanki.Model(
        model_id,
        model_name,
        fields,
        templates,
        old_card_css,
    )


_syn_config = SynthesisConfig(
    volume=1.0,
    length_scale=1.0,  # 1.2 slower
    noise_scale=0.0,  # more audio variation
    noise_w_scale=0.0,  # more speaking variation
    normalize_audio=False,  # use raw audio from voice
    # speaker_id=69,
)


def synthesize_wav(text, file_path, model_path='./de_DE-eva_k-x_low.onnx'):
    voice = PiperVoice.load(model_path)
    os.makedirs(os.path.dirname(file_path), exist_ok=True)
    with wave.open(file_path, "w") as wav_file:
        voice.synthesize_wav(text, wav_file, _syn_config)


def generate_audio(text, file_path, with_lib='piper'):
    if with_lib == 'piper':
        synthesize_wav(text, file_path)
    elif with_lib == 'coqui':
        coqui_generate_audio(text, file_path)


def add_audio(collection, model_id, model_name, old_model_fields, old_card_template, old_card_css, deck_id, deck_name,
              with_lib='piper'):
    apkg_path = f'{collection.collection_path}.apkg'
    new_apkg_path = f'{collection.collection_path}|Audio.apkg'
    extract_to = f'{collection.collection_path}_extracted'
    extract_apkg(apkg_path, extract_to)

    cur = get_cursor(collection.collection_path, collection.database_name)
    field_names = get_field_names(cur)
    cur.execute("SELECT id, guid, flds FROM notes")
    notes_data = cur.fetchall()
    print(len(notes_data))

    model = new_model(
        model_id,
        model_name,
        old_model_fields,
        old_card_template,
        old_card_css,
    )

    deck = genanki.Deck(deck_id, deck_name)
    package = genanki.Package(deck, media_files=[])

    silent_audio = './2-seconds-of-silence.mp3'
    silent_audio_tag = f'[sound:{os.path.basename(silent_audio)}]'
    package.media_files.append(silent_audio)

    total_time = 0
    for i, (note_id, guid, flds) in enumerate(notes_data):

        remaining_count = len(notes_data) - i
        print(f'Remaining item count:{remaining_count}')
        print(f'Estimated remaining time:{format_duration(remaining_count * total_time / (i + 1))}')

        fields = flds.split('\x1f')  # Fields are separated by unit separator
        new_fields = [f for f in fields]

        audio_fields = ['word_query_expanded', 'de_example_sentence_1', 'de_example_sentence_2']
        start = time.time()
        for audio_field in audio_fields:
            field_index = field_names.index(audio_field)
            field = fields[field_index]
            audio_file_path = f'./audio/{safe_filename(field)}.wav'
            if not os.path.exists(audio_file_path):
                generate_audio(field, audio_file_path, with_lib)
            audio_tag = f'[sound:{os.path.basename(audio_file_path)}]'
            new_fields.append(audio_tag)
            package.media_files.append(audio_file_path)
        new_fields.append(silent_audio_tag)
        end = time.time()
        i_time = end - start
        total_time += i_time

        new_note = genanki.Note(
            model=model,
            fields=new_fields,
        )
        deck.add_note(new_note)

    package.write_to_file(new_apkg_path)
    print(f"✅ Done! Your deck with audio 🔈 is saved as: {new_apkg_path}")
