import itertools
import os
import re
import string

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

# If modifying these scopes, delete the file token.json.
SCOPES = ['https://www.googleapis.com/auth/spreadsheets']


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

def _build_cell_notation_index():
    out = []
    for _len in range(1, 4):
        for char_tuple in itertools.product(string.ascii_uppercase, repeat=_len):
            out.append(''.join(char_tuple))
    return out


_STRING_COL_CACHE = _build_cell_notation_index()  # ['A', 'B', 'C', 'D', 'E', 'F', 'G', ...]
# noinspection PyTypeChecker
_COL_STRING_CACHE = {c: i for i, c in enumerate(_STRING_COL_CACHE)}  # {'A': 0, 'B': 1, ...}


# https://openpyxl.readthedocs.io/en/stable/_modules/openpyxl/utils/cell.html#get_column_letter
def _get_column_letter(idx: int):
    """
    Convert a column index into a column letter: (3 -> 'C')
    """
    if not isinstance(idx, int):
        raise TypeError(idx)
    elif idx <= 0:
        raise ValueError(idx)

    try:
        return _STRING_COL_CACHE[idx - 1]
    except KeyError:
        raise ValueError("Invalid column index {0}".format(idx))


def _column_index_from_string(str_col: str):
    """
    Convert a column name into a numerical index: ('A' -> 1)
    """
    # we use a function argument to get indexed name lookup
    if not isinstance(str_col, str):
        raise TypeError(str_col)
    elif not str_col:
        raise ValueError(str_col)

    try:
        return _COL_STRING_CACHE[str_col.upper()] + 1
    except KeyError:
        raise ValueError("{0} is not a valid column name".format(str_col))


def parse_column_notation(cell_address: str):
    cell_address = cell_address.upper()
    for i, char in enumerate(cell_address):
        if char.isdigit():
            if i == 0:
                raise ValueError('no row')
            if not cell_address[:i].isalpha():
                raise ValueError('invalid col')
            if not cell_address[i:].isdigit():
                raise ValueError('invalid row')
            return int(cell_address[i:]), _column_index_from_string(cell_address[:i])
    raise ValueError('no col')


def build_column_notation(row: int, column: int):
    if not isinstance(row, int):
        raise TypeError(row)
    elif row <= 0:
        raise ValueError(row)
    if not isinstance(column, int):
        raise TypeError(column)
    elif column <= 0:
        raise ValueError(column)
    return f'{_get_column_letter(column)}{row}'


class Workbook:
    def __init__(self, spreadsheet_id):

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
        self.spreadsheet_id = spreadsheet_id

    def _get_sheet_id(self, sheet_name):
        result = self.sheet.get(spreadsheetId=self.spreadsheet_id,
                                ranges=[],
                                includeGridData=False,
                                ).execute()
        return result['sheets'][0]['properties']['sheetId']

    def get_sheet_range_values(self, sheet_name, range_start, range_end):
        assert re.fullmatch(r'[A-Z]+[0-9]+', range_start)
        assert re.fullmatch(r'[A-Z]+[0-9]+', range_end)
        result = self.sheet.values().get(spreadsheetId=self.spreadsheet_id,
                                         range=f'{sheet_name}!{range_start}:{range_end}',
                                         ).execute()
        print(result.get('range'))
        print(result.get('majorDimension'))
        return result.get('values', [])

    def get_cell_properties(self, sheet_name, cell_address):
        assert re.fullmatch(r'[A-Z]+[0-9]+', cell_address)
        result = self.sheet.get(spreadsheetId=self.spreadsheet_id,
                                ranges=[f'{sheet_name}!{cell_address}'],
                                includeGridData=True,
                                ).execute()

        return {
            'properties':   result['properties'],
            'columnFormat': result['sheets'][0]['data'][0]['columnMetadata'][0],
            'cellFormat':   result['sheets'][0]['data'][0]['rowData'][0]['values'][0],
        }

    def set_cell_format(self, sheet_name, cell_row, cell_column, red, green, blue):
        body = {
            "requests": [
                {
                    "updateCells": {
                        "range":  {
                            "sheetId":          self._get_sheet_id(sheet_name),
                            "startRowIndex":    cell_row,
                            "endRowIndex":      cell_row + 1,
                            "startColumnIndex": cell_column,
                            "endColumnIndex":   cell_column + 1
                        },
                        "rows":   [
                            {
                                "values": [
                                    {
                                        "userEnteredFormat": {
                                            "backgroundColor": {
                                                "red":   red,
                                                "green": green,
                                                "blue":  blue,
                                            }
                                        }
                                    }
                                ]
                            }
                        ],
                        "fields": "userEnteredFormat.backgroundColor"
                    }
                }
            ]
        }
        return self.sheet.batchUpdate(spreadsheetId=self.spreadsheet_id, body=body).execute()


if __name__ == '__main__':
    # # https://docs.google.com/spreadsheets/d/1ahbAXvuamz2PB1COGx2dWjIV8BN75bqYL_KmgdHkWKk/edit#gid=1211096710
    # # wb = Workbook('1ahbAXvuamz2PB1COGx2dWjIV8BN75bqYL_KmgdHkWKk')
    #
    # # https://docs.google.com/spreadsheets/d/1Hx_oFmbRYRuek_eyVUyfz4_b9861mPhSBF1NHH9et70/edit#gid=1116371039
    # # wb = Workbook('1Hx_oFmbRYRuek_eyVUyfz4_b9861mPhSBF1NHH9et70')  # copy, so I don't break anything
    #
    # # https://docs.google.com/spreadsheets/d/1NeklzsZ_EZXz0W5eyPdRbZmGpNqIdAGJyIMVYO342oo/edit#gid=0
    # wb = Workbook('1NeklzsZ_EZXz0W5eyPdRbZmGpNqIdAGJyIMVYO342oo')  # random unused sheet
    #
    # # # values = wb.get_sheet_range_values('Blk 95A', 'A1', 'P29')
    # # # values = wb.get_sheet_range_values('Blk 95A', 'A11', 'B12')
    # values = wb.get_sheet_range_values('Sheet1', 'A1', 'B2')
    # if not values:
    #     print('No data found.')
    # else:
    #     for row in values:
    #         print(row)
    #
    # values = wb.get_cell_properties('Sheet1', 'B2')
    # # pprint(values['properties'])
    # pprint(values)
    #
    # values = wb.set_cell_format('Sheet1', 1, 1, 0.6, 0.6, 0.6)
    # pprint(values)

    for address in ['A1', 'B2', 'D123', 'AA1', ]:
        print(address, parse_column_notation(address))
