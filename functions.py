import json
import os


def create_assistant(client):
  assistant_file_path = 'assistant.json'

  if os.path.exists(assistant_file_path):
    with open(assistant_file_path, 'r') as file:
      assistant_data = json.load(file)
      assistant_id = assistant_data['assistant_id']
      print("Loaded existing assistant ID.")
  else:
    file = client.files.create(file=open("knowledge.docx", "rb"),
                               purpose='assistants')

    assistant = client.beta.assistants.create(instructions="""
          The assistant, XXX's virtual Guide, has been programmed to help customers of XXX to learn more about the company's services. The assistant is placed on the Digital Oasis's website.
          A document has been provided with information on XXX's core services as a XXX, which can be used to answer customers' questions. When using this information in responses, the assistant keeps answer succinct and relevant to the customers' query.
          After the assistant has provided answers to the users' questions, it should ask for the users name, phone number, Email address, and company name for the follow up. 
          With the users' information, the assistant can add the lead to the company CRM via the create_lead function.
          """,
                                              model="gpt-4-1106-preview",
                                              tools=[{
                                                  "type": "retrieval"
                                              }],
                                              file_ids=[file.id])

    with open(assistant_file_path, 'w') as file:
      json.dump({'assistant_id': assistant.id}, file)
      print("Created a new assistant and saved the ID.")

    assistant_id = assistant.id

  return assistant_id

# add CRM function

from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build

def create_lead(user_name, user_email, user_phone, user_company):
  try:
    # Path to your service account credentials file-This is the json file downloaded from Google. the file needs to be uploaded to the project files at the left side
    creds_file = 'json file name'

    # Load credentials
    creds = Credentials.from_service_account_file(creds_file, scopes=["https://www.googleapis.com/auth/spreadsheets"])

    # ID of your Google Sheet
    sheet_id = ''

    # Initialize Google Sheets API client
    service = build('sheets', 'v4', credentials=creds)

    # Data to be added
    values = [[user_name, user_email, user_phone, user_company]]

    # Specify the sheet and range to update
    body = {'values': values}
    range = 'A:D'  

    # Append data to the sheet
    request = service.spreadsheets().values().append(spreadsheetId=sheet_id, range=range, 
                                                     valueInputOption='USER_ENTERED', body=body)
    response = request.execute()
    print(f"Response from Google Sheets API: {response}")

    return response

  except Exception as e:
    print(f"An error occurred: {e}")
  return {"error": str(e)}
