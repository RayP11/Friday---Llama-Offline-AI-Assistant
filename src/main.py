"""
Main file to run Friday: A completely offline and private AI voice assistant
"""
from recognize import speak_text, listen_for_command
import json
import requests


# Initialize memory and persona
conversation_history = []
persona = """Your name is Friday, you are my personal AI assistant. I am Ray, your creator.
You will mimic human behavior through your speech as best as possible. Keep your responses brief like a human, throw in some sarcasm."""

url = "http://localhost:11434/api/generate"

data = {
    "model": "llama3.2",
}

while True:
    try:
        # Listen for audio input
        command = listen_for_command()

        if command is None:
            continue

        print(f"\nUser: {command}")
        
        # Handle Silence: Detect if no speech was detected
        if not command:
            print("No speech detected. Listening again...")
            continue

        memory = "\n".join([f"Ray: {entry['user']} You: {entry['ai']}" for entry in conversation_history])
        full_prompt = f"{persona}\n\n{memory}\nRay: {command}" if memory else f"{persona}\n\nRay: {command}"

        data["prompt"] = full_prompt

        try:
            # API request to your local server
            response = requests.post(url, json=data, stream=True)
            response.raise_for_status()
        except requests.exceptions.RequestException as e:
            print(f"Error with API request: {e}")
            continue

        if response.status_code == 200:
            ai_response = ""
            for chunk in response.iter_lines():
                if chunk:
                    decoded_chunk = chunk.decode("utf-8")
                    output = json.loads(decoded_chunk)
                    ai_response += output["response"]
                    print(output["response"], end="", flush=True)

            speak_text(ai_response)
            conversation_history.append({
                "user": command,
                "ai": ai_response,
            })

        else:
            print(f"Error: {response.status_code}")

    except Exception as e:
        print(f"Error during processing: {e}")