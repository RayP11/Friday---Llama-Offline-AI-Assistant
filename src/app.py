from recognize import speak_text, listen_for_command
import json
import requests
from flask import Flask, render_template, request, jsonify, Response
import threading
import time
import webbrowser

# Initialize memory and persona
conversation_history = []
persona = """Your name is Friday, you are my personal AI assistant. I am Ray, your creator.
You will mimic human behavior through your speech as best as possible. Keep your responses brief like a human, throw in some sarcasm."""

url = "http://localhost:11434/api/generate"

data = {
    "model": "llama3.2",
}

# Flask app setup
app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/responses', methods=['GET'])
def get_responses():
    try:
        if not conversation_history:
            return jsonify([])  # Return an empty list if no conversation history
        formatted_responses = [{"text": response["ai"]} for response in conversation_history]
        return jsonify(formatted_responses)
    except Exception as e:
        print(f"Error in /api/responses: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/stream')
def stream():
    """
    Stream new responses to the frontend via Server-Sent Events (SSE).
    """
    def generate():
        while True:
            if conversation_history:
                # Get the latest response from the conversation history
                latest_response = conversation_history[-1]["ai"]
                # Send it as an SSE event
                yield f"data: {json.dumps({'text': latest_response})}\n\n"
            time.sleep(1)  # Adjust frequency of updates as needed

    return Response(generate(), content_type='text/event-stream')

def chat():
    """
    Handles microphone input, speech, and AI responses
    """
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

            memory = "\n".join([f"Previous Messages( Ray: {entry['user']} Friday/you: {entry['ai']})" for entry in conversation_history])
            full_prompt = f"{persona}\n\n{memory}\ncurrent message( Ray: {command})" if memory else f"{persona}\n\nRay: {command}"

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
                
                conversation_history.append({
                    "user": command,
                    "ai": ai_response,
                })
                speak_text(ai_response)

            else:
                print(f"Error: {response.status_code}")

        except Exception as e:
            print(f"Error during processing: {e}")

def main():
    """
    Main function to start the user interface with the backend
    """
    # Start the Flask app in a separate thread
    threading.Thread(target=app.run, kwargs={'host': '0.0.0.0', 'port': 8000, 'debug': False}, daemon=True).start()

    # Open the user interface
    webbrowser.open('http://localhost:8000')

    # Start backend
    chat()

if __name__ == "__main__":
    main()
