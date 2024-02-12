import json
import os
from time import sleep
from packaging import version
from flask import Flask, request, jsonify
import openai
from openai import OpenAI
import functions
import flask_cors
from flask_cors import CORS


# Check OpenAI version is correct
required_version = version.parse("1.1.1")
current_version = version.parse(openai.__version__)
OPENAI_API_KEY = os.environ['OPENAI_API_KEY']
if current_version < required_version:
  raise ValueError(f"Error: OpenAI version {openai.__version__}"
                   " is less than the required version 1.1.1")
else:
  print("OpenAI version is compatible.")


# Start Flask app
app = Flask(__name__)
CORS(app)

# Init client
client = OpenAI(
    api_key=OPENAI_API_KEY)  # should use env variable OPENAI_API_KEY in secrets

# Create new assistant or load existing
assistant_id = functions.create_assistant(client)

# Start conversation thread
@app.route('/start', methods=['GET'])
def start_conversation():
  print("Starting a new conversation...")  # Debugging line
  thread = client.beta.threads.create()
  print(f"New thread created with ID: {thread.id}")  # Debugging line
  return jsonify({"thread_id": thread.id})

# Generate response
@app.route('/chat', methods=['POST'])
def chat():
  data = request.json
  thread_id = data.get('thread_id')
  user_input = data.get('message', '')

  if not thread_id:
    print("Error: Missing thread_id")  # Debugging line
    return jsonify({"error": "Missing thread_id"}), 400
  
  print(f"Received message: {user_input} for thread ID: {thread_id}"
        )  # Debugging line

  # Add the user's message to the thread
  client.beta.threads.messages.create(thread_id=thread_id,
                                      role="user",
                                      content=user_input)

  # Run the Assistant
  run = client.beta.threads.runs.create(thread_id=thread_id,
                                        assistant_id=assistant_id)

  # Check if the Run requires action (function call)
  while True:
    run_status = client.beta.threads.runs.retrieve(thread_id=thread_id,
                                                   run_id=run.id)
    print(f"Run status: {run_status.status}")
    if run_status.status == 'completed':
      break
    sleep(1)  # Wait for a second before checking again

  # Retrieve and return the latest message from the assistant
  messages = client.beta.threads.messages.list(thread_id=thread_id)
  response = messages.data[0].content[0].text.value

  print(f"Assistant response: {response}")  # Debugging line
  return jsonify({"response": response})

# Add lead to Google sheet

@app.route('/submit_user_info', methods=['POST'])

def submit_user_info():
  print("submit_user_info route called")  # Debugging line
  data = request.json
  print("Received data from Voiceflow:", data)
  user_name = data.get('name')
  user_email = data.get('email')
  user_phone = data.get('phone')
  user_company = data.get('company')
  '''thread_id = data.get('thread_id')  # Assuming you have a way to get this
    inquiry_summary = data.get('inquiry_summary')  # Summary of the user's inquiry'''

    # Now call create_lead function
  if all([user_name, user_email, user_phone, user_company]):
        functions.create_lead(user_name, user_email, user_phone, user_company)
        return jsonify({"message": "User information saved successfully"}), 200
  else:
        return jsonify({"error": "Missing information"}), 400


# Run server
if __name__ == '__main__':
  app.run(host='0.0.0.0', port=8080)
