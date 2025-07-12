import zipfile


def extract_apkg(apkg_path, extract_to='extracted_apkg'):
    with zipfile.ZipFile(apkg_path, 'r') as zip_ref:
        zip_ref.extractall(extract_to)
