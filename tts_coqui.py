from TTS.api import TTS


def coqui_generate_audio(text, file_path, model='tts_models/de/thorsten/vits'):
    print(f"Generating audio for {text}")
    tts = TTS(model)
    tts.tts_to_file(text=text, file_path=file_path)
    print("Audio generated.")
