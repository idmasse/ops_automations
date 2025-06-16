import gspread
from google.oauth2.service_account import Credentials

# google sheets API setup
def setup_google_sheets():
    scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/spreadsheets",
             "https://www.googleapis.com/auth/drive.file", "https://www.googleapis.com/auth/drive"]
    creds = Credentials.from_service_account_file('utils/gsheet_creds.json', scopes=scope)
    client = gspread.authorize(creds)
    sheet = client.open("Disputed fraud orders").worksheet('Block list phase 1')
    # banned_device_id_list = sheet.col_values(3)
    return sheet

#get list of banned device ids from column C 
def get_banned_device_ids():
    sheet = setup_google_sheets()
    banned_device_id_list = sheet.col_values(3)
    return banned_device_id_list
