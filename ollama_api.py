import requests


def call_ollama(prompt, model='gemma3:12b'):
    """
    Call local Ollama model with a prompt and return the response text.
    """
    response = requests.post(
        "http://localhost:11434/api/generate",
        json={
            "model": model,
            "prompt": prompt,
            "stream": False
        }
    )
    return response.json()['response'].strip()
