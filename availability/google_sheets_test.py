import os
import re
from pprint import pprint

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

# If modifying these scopes, delete the file token.json.
SCOPES = ['https://www.googleapis.com/auth/spreadsheets.readonly']
# Scope (https://developers.google.com/sheets/api/guides/authorizing)
#   Meaning
# https://www.googleapis.com/auth/spreadsheets.readonly
#   Allows read-only access to the user's sheets and their properties.
# https://www.googleapis.com/auth/spreadsheets
#   Allows read/write access to the user's sheets and their properties.
# https://www.googleapis.com/auth/drive.readonly
#   Allows read-only access to the user's file metadata and file content.
# https://www.googleapis.com/auth/drive.file
#   Per-file access to files created or opened by the app.
# https://www.googleapis.com/auth/drive
#   Full, permissive scope to access all of a user's files. Request this scope only when it is strictly necessary.

# https://docs.google.com/spreadsheets/d/1ahbAXvuamz2PB1COGx2dWjIV8BN75bqYL_KmgdHkWKk/edit#gid=1211096710
# spreadsheet_id = '1ahbAXvuamz2PB1COGx2dWjIV8BN75bqYL_KmgdHkWKk'

# https://docs.google.com/spreadsheets/d/1Hx_oFmbRYRuek_eyVUyfz4_b9861mPhSBF1NHH9et70/edit#gid=1116371039
spreadsheet_id = '1Hx_oFmbRYRuek_eyVUyfz4_b9861mPhSBF1NHH9et70'  # copy, so I don't break anything

# https://docs.google.com/spreadsheets/d/1NeklzsZ_EZXz0W5eyPdRbZmGpNqIdAGJyIMVYO342oo/edit#gid=0
# spreadsheet_id = '1NeklzsZ_EZXz0W5eyPdRbZmGpNqIdAGJyIMVYO342oo'  # random unused sheet


class Workbook:
    def __init__(self):

        """Shows basic usage of the Sheets API.
        Prints values from a sample spreadsheet.
        """
        creds = None

        # The file token.json stores the user's access and refresh tokens, and is
        # created automatically when the authorization flow completes for the first
        # time.
        if os.path.exists('token.json'):
            creds = Credentials.from_authorized_user_file('token.json', SCOPES)

        # If there are no (valid) credentials available, let the user log in.
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file('credentials.json', SCOPES)
                creds = flow.run_local_server(port=0)

            # Save the credentials for the next run
            with open('token.json', 'w') as token:
                token.write(creds.to_json())

        service = build('sheets', 'v4', credentials=creds)
        self.sheet = service.spreadsheets()

    def get_sheet_range_values(self, sheet_name, range_start, range_end):
        assert re.fullmatch(r'[A-Z]+[0-9]+', range_start)
        assert re.fullmatch(r'[A-Z]+[0-9]+', range_end)
        result = self.sheet.values().get(spreadsheetId=spreadsheet_id,
                                         range=f'{sheet_name}!{range_start}:{range_end}',
                                         ).execute()
        print(result.get('range'))
        print(result.get('majorDimension'))
        return result.get('values', [])

    def get_sheet_range(self, sheet_name, range_start, range_end):
        assert re.fullmatch(r'[A-Z]+[0-9]+', range_start)
        assert re.fullmatch(r'[A-Z]+[0-9]+', range_end)
        result = self.sheet.get(spreadsheetId=spreadsheet_id,
                                ranges=[f'{sheet_name}!{range_start}:{range_end}'],
                                includeGridData=True,
                                ).execute()
        print(result.get('range'))
        print(result.get('majorDimension'))
        return result.get('values', [])


if __name__ == '__main__':
    wb = Workbook()

    # values = wb.get_sheet_range_values('Blk 95A', 'A1', 'P29')
    values = wb.get_sheet_range_values('Blk 95A', 'A11', 'B12')
    if not values:
        print('No data found.')
    else:
        for row in values:
            print(row)

    values = wb.sheet.get(spreadsheetId=spreadsheet_id,
                          ranges=['Blk 95A!A11:B12'],
                          includeGridData=True).execute()
    # pprint(values['properties'])
    pprint(values['sheets'])
