import re


def safe_filename(text, replacement="_"):
    # Remove invalid characters
    return re.sub(r'[<>:"/\\|?*\n\r\t]', replacement, text).strip()
