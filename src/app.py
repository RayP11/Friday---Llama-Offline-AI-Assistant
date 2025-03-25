from recognize import speak_text, listen_for_command
import json
from flask import Flask, render_template, jsonify, Response
import threading
import time
import webbrowser
import socket
from spotify_function import play_music
from langchain.prompts import PromptTemplate
from langchain_ollama import ChatOllama
from langchain.memory import ConversationBufferMemory
from langchain.schema.output_parser import StrOutputParser
from langchain.schema.runnable import RunnablePassthrough
from langchain.schema.messages import HumanMessage, AIMessage
from get_weather import get_weather
from text_messages import send_reminder, send_message
from prompts import persona, weather_prompt, sophie_message, reminder, music_prompt
from commands import user_music, friday_music, weather_info, reminder_send, start_sleep, message_send, find_match

# Initialize memory and persona
conversation_history = []

# Initialize ChatOllama with the llama3.2 model
#model = ChatOllama(model="llama3.2")

# OR
# Initialize ChatOllama with the gemma2 model
model = ChatOllama(model="gemma2:2b")


# Initialize conversation memory
memory = ConversationBufferMemory(memory_key="chat_history", return_messages=True)

# Define the prompt template
prompt_template = PromptTemplate.from_template(
    """
    {persona}
    Chat History: {chat_history}
    Current Message: {command}
    """
)

# Helper function to format chat history
def format_chat_history(chat_history):
    formatted_history = []
    for message in chat_history:
        if isinstance(message, HumanMessage):
            formatted_history.append(f"User: {message.content}")
        elif isinstance(message, AIMessage):
            formatted_history.append(f"Friday: {message.content}")
    return "\n".join(formatted_history)

# Initialize Chain
chain = (
    {
        "persona": RunnablePassthrough(),
        "chat_history": lambda _: format_chat_history(memory.load_memory_variables({})["chat_history"]),
        "command": RunnablePassthrough(),
    }
    | prompt_template
    | model
    | StrOutputParser()
)

class FridayState:
    ACTIVE = "active"
    SLEEP = "sleep"

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

def check_internet_connection():
    try:
        # Connect to a well-known host (Google DNS) to check for internet connection
        socket.create_connection(("8.8.8.8", 53), timeout=3)
        return True
    except OSError:
        return False

def update_history(user, ai):
    # Update conversation history
                conversation_history.append({
                    "user": user,
                    "ai": ai,
                })

def ai_response(text):
    # Generate response using the chain
    ai_response_text = chain.invoke({
        "persona": persona,
        "command": text,
    })

    # Clean up the response to remove unnecessary details
    ai_response_text = ai_response_text.strip()

    update_history(text, ai_response_text)

    # Update memory
    memory.chat_memory.add_user_message(text)
    memory.chat_memory.add_ai_message(ai_response_text)
    

    return ai_response_text

def separate_response(text):
    """Same as AI_Response but with no memory added. Used for function responses not needing to be stored"""
    
    ai_response = chain.invoke({
        "persona": persona,
        "command": text,
    })
    ai_response = ai_response.strip()

    update_history(text, ai_response)

    return ai_response

def chat():
    """
    Handles microphone input, speech, and AI responses
    """
    state = FridayState.ACTIVE
    wake_word = "friday"
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
            if state == FridayState.SLEEP and wake_word in command.lower():
                state = FridayState.ACTIVE
            if state == FridayState.ACTIVE:
                if find_match(friday_music, command):
                    ai_song = ai_response(music_prompt)
                    response = play_music(ai_song)
                    update_history(command, response)
                    state = FridayState.SLEEP
                elif find_match(user_music, command):
                    response = play_music(command)
                    update_history(command, response)
                    state = FridayState.SLEEP
                elif find_match(weather_info, command):
                    weather_data = get_weather()
                    command = weather_prompt + command
                    has_forecast = False
                    for message in conversation_history:
                         if weather_data in message:
                              has_forecast = True
                              break
                    if has_forecast:
                         speak_text(ai_response(command))
                    else:
                         speak_text(ai_response(command + weather_data))
                elif find_match(reminder_send, command):
                     message = separate_response(reminder + command)
                     speak_text(message)
                     send_reminder(message)
                elif find_match(message_send, command):
                    message = separate_response(sophie_message + command)
                    speak_text(message)
                    send_message(message)
                elif find_match(start_sleep, command):
                    speak_text(ai_response(command))
                else:
                    speak_text(ai_response(command))
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