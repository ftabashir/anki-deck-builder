from TTS.utils.manage import ModelManager
from TTS.api import TTS

def generate_audio(text, file_path, model='tts_models/de/thorsten/vits'):
    print(f"Generating audio for {text}")
    tts = TTS(model)
    tts.tts_to_file(text, file_path)
    print("Audio generated.")


def download_de_models():
    manager = ModelManager()
    all_models = manager.list_models()
    german_models = [m for m in all_models if m.startswith("tts_models/de/")]
    print("German models available:")
    for m in german_models:
        print(" -", m)
    for model in german_models:
        print(f"\nDownloading {model} ...")
        model_path, config_path, model_item = manager.download_model(model)
        print(f"✅ Downloaded {model}")
        print("   Model file:", model_path)
        print("   Config file:", config_path)


if __name__ == '__main__':
    # download_de_models()

    # manager = ModelManager()
    # models = manager.list_models()
    # print(models)  # shows model names you can pick

    de_models = [
        # 'thorsten/vits',
        # 'thorsten/tacotron2-DDC',
        # 'css10/vits-neon',
        # 'thorsten/tacotron2-DCA', # How to fix "UnpicklingError: Weights only load failed"? Find TTS/utils/io.py in stacktrace and add weights_only=False to torch.load
    ]
    # for model in de_models:
    #     tts = TTS(f"tts_models/de/{model}")
    #     tts.tts_to_file(
    #         text="Für die Universität braucht man oft eine Bewerbung.",
    #         file_path=f"coqui-sample-{safe_filename(model)}.wav",
    #     )

    # Multilingual Models
    #  1: tts_models/multilingual/multi-dataset/xtts_v2
    #  2: tts_models/multilingual/multi-dataset/xtts_v1.1
    #  3: tts_models/multilingual/multi-dataset/your_tts
    #  4: tts_models/multilingual/multi-dataset/bark

    bark_model = "tts_models/multilingual/multi-dataset/bark"
    tts = TTS(bark_model)
    tts.tts_to_file(
        text="Für die Universität braucht man oft eine Bewerbung.",
        file_path="coqui-sample-bark.wav",
    )

    # # Multispeaker (e.g. VCTK dataset)
    # tts = TTS("tts_models/en/vctk/vits")
    # # List available speakers
    # print(tts.speakers)
    # # Use a specific speaker
    # tts.tts_to_file(
    #     text="Hi, I'm speaking with a different voice!",
    #     speaker=tts.speakers[10],  # pick a speaker index or name
    #     file_path="speaker_output.wav"
    # )

    # # For voice cloning you’ll need a voice sample(wav file)
    # tts = TTS("tts_models/multilingual/multi-dataset/your_tts")
    # tts.tts_to_file(
    #     text="This is cloned speech.",
    #     speaker_wav="path_to_sample.wav",
    #     file_path="cloned_output.wav"
    # )
