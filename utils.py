import zipfile
import os

def save_tale_text(tale, filename):
    with open(filename, 'w', encoding='utf-8') as f:
        f.write(tale)
    return filename

def save_audio_file(audio_bytes, filename):
    with open(filename, 'wb') as f:
        f.write(audio_bytes)
    return filename

def zip_tale_and_audio(tale_path, audio_path, zip_path):
    with zipfile.ZipFile(zip_path, 'w') as zf:
        zf.write(tale_path, os.path.basename(tale_path))
        zf.write(audio_path, os.path.basename(audio_path))
    return zip_path
