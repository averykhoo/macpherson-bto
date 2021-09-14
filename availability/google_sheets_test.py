import itertools
import operator
import os
import re
import string
from pprint import pprint
from typing import Dict
from typing import Optional
from typing import Union

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


_STRING_COL_CACHE = [''.join(x) for i in range(1, 4) for x in itertools.product(string.ascii_uppercase, repeat=i)]
# noinspection PyTypeChecker
_COL_STRING_CACHE = {c: i for i, c in enumerate(_STRING_COL_CACHE)}  # {'A': 0, 'B': 1, ...}


# https://openpyxl.readthedocs.io/en/stable/_modules/openpyxl/utils/cell.html#get_column_letter
def _get_column_letter(idx: int):
    """
    Convert a column index into a column letter: 2 -> 'B'
    One-indexed
    Column between 1 and 18278 inclusive
    >>> _get_column_letter(1)
    'A'
    >>> _get_column_letter(27)
    'AA'
    """
    if not isinstance(idx, int):
        raise TypeError(idx)
    elif idx <= 0:
        raise ValueError(idx)
    elif idx > 18278:
        raise ValueError(idx)

    try:
        return _STRING_COL_CACHE[idx - 1]
    except KeyError:
        raise ValueError("Invalid column index {0}".format(idx))


def _column_index_from_string(str_col: str):
    """
    Convert a column name into a numerical index: 'B' -> 2
    One-indexed
    Column between A and ZZZ inclusive
    >>> _column_index_from_string('A')
    1
    >>> _column_index_from_string('AA')
    27
    """
    # we use a function argument to get indexed name lookup
    if not isinstance(str_col, str):
        raise TypeError(str_col)
    elif not str_col:
        raise ValueError(str_col)
    elif len(str_col) > 3:
        raise ValueError(str_col)

    try:
        return _COL_STRING_CACHE[str_col.upper()] + 1
    except KeyError:
        raise ValueError("{0} is not a valid column name".format(str_col))


def parse_column_notation(cell_address: str, zero_index: bool = False):
    """
    Convert R1C1 to coordinates: 'B7' -> (7, 2)
    One-indexed
    Column between A and ZZZ inclusive
    >>> parse_column_notation('A2')
    (2, 1)
    >>> parse_column_notation('AA22')
    (22, 27)
    >>> parse_column_notation('A1', zero_index=True)
    (0, 0)
    >>> parse_column_notation('Z10', zero_index=True)
    (9, 25)
    """
    if not isinstance(cell_address, str):
        raise TypeError(cell_address)
    cell_address = cell_address.upper()
    for i, char in enumerate(cell_address):
        if char.isdigit():
            if i == 0:
                raise ValueError(f'no row: {cell_address}')
            if not cell_address[:i].isalpha():
                raise ValueError(f'invalid col: {cell_address[:i]}')
            if i > 3:
                raise ValueError(f'col too large, not supported: {cell_address[:i]}')
            if not cell_address[i:].isdigit():
                raise ValueError(f'invalid row: {cell_address[i:]}')
            if zero_index:
                return int(cell_address[i:]) - 1, _column_index_from_string(cell_address[:i]) - 1
            else:
                return int(cell_address[i:]), _column_index_from_string(cell_address[:i])
    raise ValueError(f'no col: {cell_address}')


def build_column_notation(row: int, column: int):
    """
    Convert coordinates to R1C1: (7, 2) -> 'B7'
    One-indexed
    Column between 1 and 18278 inclusive
    >>> build_column_notation(2, 1)
    'A2'
    >>> build_column_notation(22, 27)
    'AA22'
    """
    if not isinstance(row, int):
        raise TypeError(row)
    elif row <= 0:
        raise ValueError(row)
    if not isinstance(column, int):
        raise TypeError(column)
    elif column <= 0:
        raise ValueError(column)
    elif column > 18278:
        raise ValueError(column)
    return f'{_get_column_letter(column)}{row}'


def color_hex_to_float(color_hex: str) -> Dict[str, float]:
    """
    >>> color_hex_to_float('#000000')
    {'red': 0.0, 'green': 0.0, 'blue': 0.0}
    >>> color_hex_to_float('#333333')
    {'red': 0.2, 'green': 0.2, 'blue': 0.2}
    >>> color_hex_to_float('#FF0000')
    {'red': 1.0, 'green': 0.0, 'blue': 0.0}
    >>> color_hex_to_float('#00FF00')
    {'red': 0.0, 'green': 1.0, 'blue': 0.0}
    >>> color_hex_to_float('#0000FF')
    {'red': 0.0, 'green': 0.0, 'blue': 1.0}
    >>> color_hex_to_float('#FFFFFF')
    {'red': 1.0, 'green': 1.0, 'blue': 1.0}
    >>> color_hex_to_float('#ffffff')
    {'red': 1.0, 'green': 1.0, 'blue': 1.0}
    >>> color_hex_to_float('FFFFFF')
    {'red': 1.0, 'green': 1.0, 'blue': 1.0}
    >>> color_hex_to_float('#000')
    {'red': 0.0, 'green': 0.0, 'blue': 0.0}
    >>> color_hex_to_float('#333')
    {'red': 0.2, 'green': 0.2, 'blue': 0.2}
    >>> color_hex_to_float('#F00')
    {'red': 1.0, 'green': 0.0, 'blue': 0.0}
    >>> color_hex_to_float('#0F0')
    {'red': 0.0, 'green': 1.0, 'blue': 0.0}
    >>> color_hex_to_float('#00F')
    {'red': 0.0, 'green': 0.0, 'blue': 1.0}
    >>> color_hex_to_float('#FFF')
    {'red': 1.0, 'green': 1.0, 'blue': 1.0}
    >>> color_hex_to_float('#fff')
    {'red': 1.0, 'green': 1.0, 'blue': 1.0}
    >>> color_hex_to_float('FFF')
    {'red': 1.0, 'green': 1.0, 'blue': 1.0}
    """
    if not isinstance(color_hex, str):
        raise TypeError(color_hex)
    if color_hex[0] == '#':
        _rr_gg_bb = color_hex[1:].strip()
    else:
        _rr_gg_bb = color_hex.strip()

    # if parsing fails, this isn't a hex int
    _rgb_int = int(_rr_gg_bb, 16)

    # parse #FFFFFF
    if len(_rr_gg_bb) == 6:
        blue = float(_rgb_int & 0xFF) / 0xFF
        _rgb_int >>= 8
        green = float(_rgb_int & 0xFF) / 0xFF
        _rgb_int >>= 8
        red = float(_rgb_int & 0xFF) / 0xFF
        assert _rgb_int >> 8 == 0

    # parse #FFF
    elif len(_rr_gg_bb) == 3:
        blue = float(_rgb_int & 0xF) / 0xF
        _rgb_int >>= 4
        green = float(_rgb_int & 0xF) / 0xF
        _rgb_int >>= 4
        red = float(_rgb_int & 0xF) / 0xF
        assert _rgb_int >> 4 == 0

    # invalid
    else:
        raise ValueError(color_hex)

    # return a dict that can be easily converted to kwargs
    return {
        'red':   red,
        'green': green,
        'blue':  blue,
    }


def color_float_to_hex(*, red: float = 0.0, green: float = 0.0, blue: float = 0.0) -> str:
    """
    >>> color_float_to_hex(red=1, green=0.8509804, blue=0)
    '#FFD900'
    """
    if not isinstance(red, (int, float)):
        raise TypeError(red)
    if not isinstance(green, (int, float)):
        raise TypeError(green)
    if not isinstance(blue, (int, float)):
        raise TypeError(blue)
    if not 0.0 <= red <= 1.0:
        raise ValueError(red)
    if not 0.0 <= green <= 1.0:
        raise ValueError(green)
    if not 0.0 <= blue <= 1.0:
        raise ValueError(blue)

    return f'#{round(red * 0xFF):02X}{round(green * 0xFF):02X}{round(blue * 0xFF):02X}'


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

    def _get_sheet_names_and_ids(self) -> Dict[str, int]:
        result = self.sheet.get(spreadsheetId=self.spreadsheet_id,
                                ranges=[],
                                includeGridData=False,
                                ).execute()
        return {sheet['properties']['title']: sheet['properties']['sheetId'] for sheet in result['sheets']}

    def _get_sheet_id(self, sheet_name) -> int:
        """
        sheet names are case-insensitive but space-sensitive
        only spaces are allowed, not other whitespace
        """
        if not isinstance(sheet_name, str):
            raise TypeError
        if not sheet_name or any(char in sheet_name for char in '\v\t\f\r\n'):
            raise ValueError(sheet_name)
        sheet_name_ids = self._get_sheet_names_and_ids()
        for actual_sheet_name, actual_sheet_id in sheet_name_ids.items():
            if sheet_name.casefold() == actual_sheet_name.casefold():
                return actual_sheet_id
        raise IndexError(f'"{sheet_name}" not in {sheet_name_ids.keys()}')

    def _get_sheet_range(self, sheet_name, range_start, range_end=None):
        start_row, start_column = parse_column_notation(range_start, zero_index=True)
        end_row, end_column = parse_column_notation(range_end or range_start)
        return {"sheetId":          self._get_sheet_id(sheet_name),
                "startRowIndex":    start_row,
                "endRowIndex":      end_row,
                "startColumnIndex": start_column,
                "endColumnIndex":   end_column,
                }

    def get_sheet_range_values(self, sheet_name, range_start, range_end):
        assert re.fullmatch(r'[A-Z]+[0-9]+', range_start)
        assert re.fullmatch(r'[A-Z]+[0-9]+', range_end)
        result = self.sheet.values().get(spreadsheetId=self.spreadsheet_id,
                                         range=f'{sheet_name}!{range_start}:{range_end}',
                                         ).execute()
        # print(result.get('range'))
        # print(result.get('majorDimension'))
        return result.get('values', [])

    def get_properties(self, sheet_name, cell_address):
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

    def get_background_color(self, sheet_name, cell_address):
        _props = self.get_properties(sheet_name, cell_address)
        return color_float_to_hex(**_props['cellFormat']['effectiveFormat']['backgroundColor'])

    def get_text_color(self, sheet_name, cell_address):
        _props = self.get_properties(sheet_name, cell_address)
        return color_float_to_hex(**_props['cellFormat']['effectiveFormat']['textFormat']['foregroundColor'])

    def get_value(self, sheet_name, cell_address):
        assert re.fullmatch(r'[A-Z]+[0-9]+', cell_address)
        result = self.sheet.values().get(spreadsheetId=self.spreadsheet_id,
                                         range=f'{sheet_name}!{cell_address}',
                                         ).execute()
        # print(result.get('range'))
        # print(result.get('majorDimension'))
        return result.get('values', [])[0][0]

    def set_background_color(self,
                             sheet_name: str,
                             cell_address: str,
                             color_hex: Optional[str] = None,
                             ):
        if color_hex is not None:
            red, green, blue = operator.itemgetter('red', 'green', 'blue')(color_hex_to_float(color_hex))
        else:
            red = green = blue = 1.0  # default white

        body = {
            "requests": [
                {
                    "updateCells": {
                        "range":  self._get_sheet_range(sheet_name, cell_address),
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

    def set_text_format(self,
                        sheet_name,
                        cell_address,
                        color_hex: Optional[str] = None,
                        *,
                        bold: Optional[bool] = None,
                        italic: Optional[bool] = None,
                        underline: Optional[bool] = None,
                        strikethrough: Optional[bool] = None,
                        font_size: Optional[Union[float, int]] = None,
                        ):
        if color_hex is not None:
            red, green, blue = operator.itemgetter('red', 'green', 'blue')(color_hex_to_float(color_hex))
        else:
            red = green = blue = None  # default black

        body = {
            "requests": [
                {
                    "updateCells": {
                        "range":  self._get_sheet_range(sheet_name, cell_address),
                        "rows":   [
                            {
                                "values": [
                                    {
                                        "userEnteredFormat": {
                                            "textFormat": {
                                                "foregroundColor": {
                                                    "red":   red,
                                                    "green": green,
                                                    "blue":  blue,
                                                },
                                                "fontSize":        font_size,
                                                "bold":            bold,
                                                "italic":          italic,
                                                "underline":       underline,
                                                "strikethrough":   strikethrough,
                                            }
                                        }
                                    }
                                ]
                            }
                        ],
                        "fields": "userEnteredFormat.textFormat"
                        # "fields": "userEnteredFormat(backgroundColor,textFormat,horizontalAlignment)"
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
    # wb = Workbook('1Hx_oFmbRYRuek_eyVUyfz4_b9861mPhSBF1NHH9et70')  # copy, so I don't break anything
    #
    # # https://docs.google.com/spreadsheets/d/1NeklzsZ_EZXz0W5eyPdRbZmGpNqIdAGJyIMVYO342oo/edit#gid=0
    wb = Workbook('1NeklzsZ_EZXz0W5eyPdRbZmGpNqIdAGJyIMVYO342oo')  # random unused sheet
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

    # wb.set_background_color('Sheet1', 'B2', color_hex='#999')
    # wb.set_background_color('Sheet1', 'B2', color_hex='#d9d9d9')
    # wb.set_text_format('Sheet1', 'B2', color_hex='#0ff')
    wb.set_background_color('Sheet1', 'B2')
    wb.set_text_format('Sheet1', 'B2')

    print('value=', wb.get_value('Sheet1', 'B2'))
    print('text_color=', wb.get_text_color('Sheet1', 'B2'))
    print('background_color=', wb.get_background_color('Sheet1', 'B2'))
