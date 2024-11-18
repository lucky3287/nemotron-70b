import json
import streamlit as st
from openai import OpenAI

# Initialize the OpenAI client
client = OpenAI(
    base_url="https://integrate.api.nvidia.com/v1",
    api_key="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"
)

# Load the output.json file or initialize an empty dictionary if it doesn't exist
try:
    with open('output.json', 'r') as file:
        responses = json.load(file)
except FileNotFoundError:
    responses = {}  # Initialize an empty dictionary if the file does not exist
except json.JSONDecodeError:
    print("Error decoding JSON from output.json. Starting with an empty dictionary.")
    responses = {}

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

# Streamlit user interface
def chatbot_ui():
    st.title("Chatbot Interface")
    st.write("Hello! I'm your chatbot. Type your command below.")

    user_input = st.text_input("You:", "")
    
    if st.button("Send"):
        if user_input.lower().strip() == 'exit':
            st.write("chatbot: Goodbye!")
            st.stop()
        
        # Check if the command is in the responses dictionary
        if user_input in responses:
            answer = responses[user_input]
            st.write(f"chatbot: {answer}")
        else:
            # Generate a response using the OpenAI client
            nvidia_answer = answer_to_query(user_input)
            st.write(f"chatbot: {nvidia_answer}")
            # Save the new chat entry to the JSON file
            save_chat_to_json(user_input, nvidia_answer)

if __name__ == "__main__":
    chatbot_ui()