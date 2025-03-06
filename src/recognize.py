"""
Includes functions to recognize speech and give audio output for responses
"""

import whisper
import pyttsx3
import speech_recognition as sr
import os
import tempfile
import requests

# Initialize Whisper model for offline transcription
model = whisper.load_model("base")

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
    engine.setProperty('voice', voices[1].id)
    engine.setProperty('rate', 187)
    engine.setProperty('volume', 1.0)
    engine.say(text)
    engine.runAndWait()

def is_valid_command(command):
    """
    Validates the transcription to ensure no background noise is recognized.
    """
    # Ignore short or overly long commands: Needed in order to account for non-speech noise
    if len(command) < 11 or len(command) > 100:
        return False
    return True

def is_connected_to_internet():
    """
    Checks if the system is connected to the internet.
    """
    try:
        requests.get("https://www.google.com", timeout=5)
        return True
    except requests.ConnectionError:
        return False

def listen_for_command():
    """
    Listens for audio input, processes it with Google Speech Recognition if online,
    or with Whisper if offline, and returns the command text.
    """
    with source as s:
        print("\nListening for commands...")
        recognizer.adjust_for_ambient_noise(source, duration=0.8)  # Adjust for ambient noise
        try:
            # Listen for up to 5 seconds of silence or until speech ends
            audio = recognizer.listen(source, timeout=5, phrase_time_limit=12)
            print("Audio captured successfully.")
        except sr.WaitTimeoutError:
            print("No speech detected within 5 seconds.")
            return None
        except Exception as e:
            print(f"Error during listening: {e}")
            return None

    try:
        if is_connected_to_internet():
            print("Using Google Speech Recognition...")
            command = recognizer.recognize_google(audio).strip().lower()
            print(f"Google Recognition Result: {command}")
        else:
            print("Using Whisper for offline transcription...")
            with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as temp_audio_file:
                temp_audio_file.write(audio.get_wav_data())
                temp_audio_file.close()

                audio_array = whisper.load_audio(temp_audio_file.name)
                result = model.transcribe(audio_array)
                command = result["text"].strip().lower()
                print(f"Whisper Recognition Result: {command}")
                os.remove(temp_audio_file.name)

        if is_valid_command(command):
            return command
        else:
            print("No valid speech detected.")
            return None

    except sr.UnknownValueError:
        print("Google Speech Recognition could not understand the audio.")
        return None
    except sr.RequestError as e:
        print(f"Could not request results from Google Speech Recognition service; {e}")
        return None
    except Exception as e:
        print(f"Error during transcription: {e}")
        return None

#testing
if __name__ == "__main__":
    command = listen_for_command()
    if command:
        print(f"Command recognized: {command}")
        speak_text(f"You said: {command}")
    else:
        print("No valid command recognized.")