from recognize import speak_text, listen_for_command
import json
from flask import Flask, render_template, jsonify, Response
import threading
import time
import webbrowser
from spotify_function import play_music
from langchain.prompts import PromptTemplate
from langchain_ollama import ChatOllama  # Use ChatOllama for better integration
from langchain.memory import ConversationBufferMemory
from langchain.schema.output_parser import StrOutputParser
from langchain.schema.runnable import RunnablePassthrough
from langchain.schema.messages import HumanMessage, AIMessage  # Import message types

# Initialize memory and persona
conversation_history = []
persona = """Your name is Friday, you are my personal AI assistant. I am Ray, your creator.
You will mimic human behavior through your speech as best as possible. Keep your responses brief and friendly, throw in a bit of sarcasm.
You have the ability to play music on spotify when connected to wifi, when I tell you to play music (ex. "play back in black" or "play me a song") just give me the name of the song and only the song name as your response, don't say the artist name either.
My music preferences include, classic rock, rap, and alternative. 
Your goal is to assist me with whatever I need"""

# Initialize ChatOllama with the llama3.2 model
model = ChatOllama(model="llama3.2")

# Initialize conversation memory
memory = ConversationBufferMemory(memory_key="chat_history", return_messages=True)

# Define the prompt template
prompt_template = PromptTemplate.from_template(
    """
    <s> [INST] 
    {persona}
    Chat History: {chat_history}
    Current Message: {command}
    [/INST] </s>
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
                # Generate response using the chain
                ai_response = chain.invoke({
                    "persona": persona,
                    "command": command,
                })

                # Update conversation history
                conversation_history.append({
                    "user": command,
                    "ai": ai_response,
                })

                # Update memory
                memory.chat_memory.add_user_message(command)
                memory.chat_memory.add_ai_message(ai_response)

                if "music" in command.lower():
                    play_music(ai_response)
                    state = FridayState.SLEEP
                elif "play" in command.lower():
                    play_music(command)
                    state = FridayState.SLEEP
                elif "that's all" in command.lower():
                    speak_text(ai_response)
                    state = FridayState.SLEEP
                else:
                    speak_text(ai_response)
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