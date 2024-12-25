from flask import Flask, request, jsonify, render_template
import json
from openai import OpenAI

app = Flask(__name__)

# Initialize the OpenAI client
client = OpenAI(
    base_url="https://integrate.api.nvidia.com/v1",
    api_key="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"
)

# Load the output.json file or initialize an empty dictionary if it doesn't exist
try:
    with open('output.json', 'r') as file:
        responses = json.load(file)
except (FileNotFoundError, json.JSONDecodeError):
    responses = {}  # Initialize an empty dictionary if the file does not exist or is invalid

def save_chat_to_json(user_input, bot_response):
    # Append the new chat entry to the responses dictionary
    responses[user_input] = bot_response
    # Write the updated responses back to the output.json file
    with open('output.json', 'w') as file:
        json.dump(responses, file, indent=4)

def answer_to_query(query):
    completion = client.chat.completions.create(
        model="nvidia/llama-3.1-nemotron-70b-instruct",
        messages=[{"role": "user", "content": "answer " + query + " in short sentence"}],
        temperature=0.5,
        top_p=1,
        max_tokens=1024,
        stream=True
    )

    full_answer = ""  # Initialize an empty string to accumulate the response

    for chunk in completion:
        if chunk.choices and chunk.choices[0].delta.content is not None:
            full_answer += chunk.choices[0].delta.content  # Concatenate each chunk to the full answer

    return full_answer if full_answer else "No response received."  # Return full answer or a fallback message

@app.route('/')
def index():
    return render_template('index.html')  # Serve the HTML template for the chatbot interface

@app.route('/chat', methods=['POST'])
def chat():
    user_input = request.json.get('user_input')
    if not user_input:
        return jsonify({"error": "No input provided."}), 400

    if user_input.lower().strip() == 'exit':
        return jsonify({"response": "Goodbye!"})

    # Check if the command is in the responses dictionary
    if user_input in responses:
        answer = responses[user_input]
    else:
        # Generate a response using the OpenAI client
        answer = answer_to_query(user_input)
        # Save the new chat entry to the JSON file
        save_chat_to_json(user_input, answer)

    return jsonify({"response": answer})

if __name__ == "__main__":
    app.run(debug=True)
