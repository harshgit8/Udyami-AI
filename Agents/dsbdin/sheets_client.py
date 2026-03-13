from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
import config

SCOPES = ['https://www.googleapis.com/auth/spreadsheets']

class SheetsClient:
    def __init__(self):
        import os
        if not os.path.exists(config.SERVICE_ACCOUNT_FILE):
            raise FileNotFoundError(
                f"Service account file not found: {config.SERVICE_ACCOUNT_FILE}\n"
                f"Download from Google Cloud Console:\n"
                f"1. Go to https://console.cloud.google.com/iam-admin/serviceaccounts\n"
                f"2. Create/select service account\n"
                f"3. Create key (JSON format)\n"
                f"4. Save as 'creds.json' in project root"
            )
        creds = service_account.Credentials.from_service_account_file(
            config.SERVICE_ACCOUNT_FILE, scopes=SCOPES)
        self.service = build('sheets', 'v4', credentials=creds)
        self.sheet_id = config.GOOGLE_SHEET_ID
    
    def read_sheet(self, range_name):
        try:
            result = self.service.spreadsheets().values().get(
                spreadsheetId=self.sheet_id, range=range_name).execute()
            return result.get('values', [])
        except HttpError as e:
            if e.resp.status == 400 and "Unable to parse range" in str(e):
                sheet_metadata = self.service.spreadsheets().get(
                    spreadsheetId=self.sheet_id).execute()
                sheets = sheet_metadata.get('sheets', [])
                available_tabs = [s['properties']['title'] for s in sheets]
                raise Exception(
                    f"Sheet tab not found. Available tabs: {', '.join(available_tabs)}\n"
                    f"Update SHEET_NAME in .env to match one of these tabs."
                )
            raise Exception(f"Failed to read sheet: {e}")
    
    def write_sheet(self, range_name, values):
        try:
            body = {'values': values}
            self.service.spreadsheets().values().update(
                spreadsheetId=self.sheet_id, range=range_name,
                valueInputOption='RAW', body=body).execute()
        except HttpError as e:
            raise Exception(f"Failed to write sheet: {e}")
    
    def append_sheet(self, range_name, values):
        try:
            body = {'values': values}
            self.service.spreadsheets().values().append(
                spreadsheetId=self.sheet_id, range=range_name,
                valueInputOption='RAW', body=body).execute()
        except HttpError as e:
            raise Exception(f"Failed to append sheet: {e}")
