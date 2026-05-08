from gtts import gTTS
import hashlib
import os

# Folder to store cached audio
CACHE_FOLDER = "bengali_audio_cache"

# Create folder if not exists
os.makedirs(CACHE_FOLDER, exist_ok=True)


def generate_bengali_audio(text):

    # Create unique filename using hash
    text_hash = hashlib.md5(
        text.encode()
    ).hexdigest()

    file_name = f"{text_hash}.mp3"

    file_path = os.path.join(
        CACHE_FOLDER,
        file_name
    )

    # If audio already exists → reuse
    if os.path.exists(file_path):

        return file_path

    # Otherwise generate new audio
    tts = gTTS(

        text=text,
        lang="bn",
        slow=False

    )

    tts.save(file_path)

    return file_path