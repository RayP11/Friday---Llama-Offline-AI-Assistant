"""
Includes functions to recognize speech and give audio output for responses
"""

import whisper
import pyttsx3
import speech_recognition as sr
import os
import tempfile
import re

# Initialize Whisper model for offline transcription
model = whisper.load_model("small")

# Initialize Speech Recognition
recognizer = sr.Recognizer()
source = sr.Microphone()

# Initialize pyttsx3 for speech output
def speak_text(text):
    """
    Takes in text to speak with Sapi-5 voice for Windows machine
    """
    engine = pyttsx3.init()
    voices = engine.getProperty('voices')
    engine.setProperty('voice', voices[1].id)  # Adjust to preferred voice
    engine.setProperty('rate', 187)
    engine.setProperty('volume', 1.0)
    engine.say(text)
    engine.runAndWait()

def is_valid_command(command):
    """
    Validates the transcription to ensure no background noise is recognized.
    """
    # # Ensure it contains valid alphabetic characters (ignore gibberish or symbols)
    # if not re.match(r"^[a-zA-Z0-9\s,.!'-]$", command):
    #     return False
    # Ignore short or overly long commands: Needed in order to account for non-speech noise
    if len(command) < 11 or len(command) > 100:
        return False
    return True

def listen_for_command():
    """
    Listens for audio input, processes it with Whisper, and returns the command text.
    """
    with source as s:
        print("\nListening for commands...")
        recognizer.adjust_for_ambient_noise(source)
        try:
            audio = recognizer.listen(source, timeout=5)  # Wait for up to 5 seconds to capture input
        except Exception as e:
            print(f"Error during listening: {e}")
            return None

    try:
        # Save audio to a temporary file
        with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as temp_audio_file:
            temp_audio_file.write(audio.get_wav_data())
            temp_audio_file.close()

            # Load the audio file into Whisper
            audio_array = whisper.load_audio(temp_audio_file.name)
            result = model.transcribe(audio_array)

            command = result["text"].strip().lower()
            os.remove(temp_audio_file.name)  # Clean up the temporary audio file

            if is_valid_command(command):
                return command
            else:
                print("No speech detected...")
                return None

    except Exception as e:
        print(f"Error during transcription: {e}")
        return None