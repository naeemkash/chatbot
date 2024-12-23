import requests
from itertools import zip_longest
import streamlit as st
from streamlit_chat import message
from langchain.schema import (
    SystemMessage,
    HumanMessage,
    AIMessage
)

# Google Gemini API Key
Google_Gemini_API = st.secrets["Google_Gemini_API"]
api_url = "https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent"  # Use the correct URL for Gemini API

# Set streamlit page configuration
st.set_page_config(page_title="Hope to Skill ChatBot")
st.title("AI Mentor")

# Initialize session state variables
if 'generated' not in st.session_state:
    st.session_state['generated'] = []  # Store AI generated responses

if 'past' not in st.session_state:
    st.session_state['past'] = []  # Store past user inputs

if 'entered_prompt' not in st.session_state:
    st.session_state['entered_prompt'] = ""  # Store the latest user input


def build_message_list():
    """
    Build a list of messages including system, human and AI messages.
    """
    # Start zipped_messages with the SystemMessage
    zipped_messages = [SystemMessage(
        content = """your name is AI Mentor. You are an AI Technical Expert for Artificial Intelligence, here to guide and assist students with their AI-related questions and concerns. Please provide accurate and helpful information, and always maintain a polite and professional tone."""
    )]

    # Zip together the past and generated messages
    for human_msg, ai_msg in zip_longest(st.session_state['past'], st.session_state['generated']):
        if human_msg is not None:
            zipped_messages.append(HumanMessage(content=human_msg))  # Add user messages
        if ai_msg is not None:
            zipped_messages.append(AIMessage(content=ai_msg))  # Add AI messages

    return zipped_messages


def generate_response():
    """
    Generate AI response using the Google Gemini API.
    """
    # Get the messages to send to Gemini
    messages = build_message_list()
    user_message = messages[-1].content  # Get the latest user message

    # API request to Google Gemini
    headers = {
        "Authorization": f"Bearer {Google_Gemini_API}",
        "Content-Type": "application/json"
    }
    data = {
        "input": user_message,  # Pass the user message to the API
        "max_tokens": 100,  # Limit the response length
        "temperature": 0.5  # Set the response creativity
    }

    response = requests.post(api_url, headers=headers, json=data)

    if response.status_code == 200:
        # Extract and return the AI response
        return response.json().get('output', 'کوئی جواب نہیں ملا.')
    else:
        # Return error message if the request fails
        return f"Error: {response.status_code}, {response.text}"


# Define function to submit user input
def submit():
    # Set entered_prompt to the current value of prompt_input
    st.session_state.entered_prompt = st.session_state.prompt_input
    # Clear prompt_input
    st.session_state.prompt_input = ""


# Create a text input for user
st.text_input('YOU: ', key='prompt_input', on_change=submit)


if st.session_state.entered_prompt != "":
    # Get user query
    user_query = st.session_state.entered_prompt

    # Append user query to past queries
    st.session_state.past.append(user_query)

    # Generate response
    output = generate_response()

    # Append AI response to generated responses
    st.session_state.generated.append(output)


# Display the chat history
if st.session_state['generated']:
    for i in range(len(st.session_state['generated'])-1, -1, -1):
        # Display AI response
        message(st.session_state["generated"][i], key=str(i))
        # Display user message
        message(st.session_state['past'][i], is_user=True, key=str(i) + '_user')
