from googleapiclient.discovery import build
from google.oauth2.service_account import Credentials

def test_google_sheets_connection():
    creds_file = '.json'
    creds = Credentials.from_service_account_file(creds_file, scopes=["https://www.googleapis.com/auth/spreadsheets"])
    service = build('sheets', 'v4', credentials=creds)

    # Replace with your sheet ID
    sheet_id = ''  
    range = 'Sheet1!A1'

    # Read the content of cell A1
    result = service.spreadsheets().values().get(spreadsheetId=sheet_id, range=range).execute()
    print(result.get('values', []))

# Call the test function
test_google_sheets_connection()
