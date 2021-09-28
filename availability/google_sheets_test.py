import itertools
import operator
import os
import re
import string
import time
from dataclasses import dataclass
from pprint import pprint
from typing import Dict
from typing import List
from typing import Optional
from typing import Union

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

from availability.color_distance import nearest_color_name

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


def color_hex_to_name(color_hex):
    r, g, b = operator.itemgetter('red', 'green', 'blue')(color_hex_to_float(color_hex))
    return nearest_color_name((r * 0xFF, g * 0xFF, b * 0xFF))


class Sheet:
    def __init__(self, spreadsheet_id, sheet_name):

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
        self.sheet_service = service.spreadsheets()
        self.spreadsheet_id = spreadsheet_id
        self.sheet_name = sheet_name
        self._get_sheet_id()  # test sheet name exists

    def __get_workbook_sheet_names_and_ids(self) -> Dict[str, int]:
        result = self.sheet_service.get(spreadsheetId=self.spreadsheet_id,
                                        ranges=[],
                                        includeGridData=False,
                                        ).execute()
        time.sleep(1)
        return {sheet['properties']['title']: sheet['properties']['sheetId'] for sheet in result['sheets']}

    def _get_sheet_id(self) -> int:
        """
        sheet_service names are case-insensitive but space-sensitive
        only spaces are allowed, not other whitespace
        """
        if not isinstance(self.sheet_name, str):
            raise TypeError
        if not self.sheet_name or any(char in self.sheet_name for char in '\v\t\f\r\n'):
            raise ValueError(self.sheet_name)
        sheet_name_ids = self.__get_workbook_sheet_names_and_ids()
        for actual_sheet_name, actual_sheet_id in sheet_name_ids.items():
            if self.sheet_name.casefold() == actual_sheet_name.casefold():
                return actual_sheet_id
        raise IndexError(f'"{self.sheet_name}" not in {sheet_name_ids.keys()}')

    def _get_sheet_range(self, range_start, range_end=None):  # todo: range_address instead
        start_row, start_column = parse_column_notation(range_start, zero_index=True)
        end_row, end_column = parse_column_notation(range_end or range_start)
        return {"sheetId":          self._get_sheet_id(),
                "startRowIndex":    start_row,
                "endRowIndex":      end_row,
                "startColumnIndex": start_column,
                "endColumnIndex":   end_column,
                }

    def set_sheet_dimensions(self, num_rows, num_columns):
        # https://stackoverflow.com/questions/61791361/how-to-resize-a-worksheet-with-the-google-client-library
        body = {"requests": [{"updateSheetProperties": {
            "properties": {
                "gridProperties": {
                    "rowCount":    num_rows,
                    "columnCount": num_columns
                }, "sheetId":     self._get_sheet_id(),
            }, "fields":  "gridProperties"
        }}]}
        self.sheet_service.batchUpdate(spreadsheetId=self.spreadsheet_id,
                                       body=body).execute()

    def append_sheet_dimensions(self, additional_rows, additional_columns):
        # https://stackoverflow.com/questions/61791361/how-to-resize-a-worksheet-with-the-google-client-library
        body = {"requests": [{"appendDimension": {
            "sheetId":   self._get_sheet_id(),
            "dimension": "ROWS",
            "length":    additional_rows
        }},
            {"appendDimension": {
                "sheetId":   self._get_sheet_id(),
                "dimension": "COLUMNS",
                "length":    additional_columns
            }}]}
        self.sheet_service.batchUpdate(spreadsheetId=self.spreadsheet_id,
                                       body=body).execute()

    def get_sheet_range_values(self, range_start, range_end):  # todo: range_address instead
        assert re.fullmatch(r'[A-Z]+[0-9]+', range_start)
        assert re.fullmatch(r'[A-Z]+[0-9]+', range_end)
        result = self.sheet_service.values().get(spreadsheetId=self.spreadsheet_id,
                                                 range=f'{self.sheet_name}!{range_start}:{range_end}',
                                                 ).execute()
        time.sleep(1)
        # print(result.get('range'))
        # print(result.get('majorDimension'))
        return result.get('values', [])

    def get_properties(self, cell_address):
        assert re.fullmatch(r'[A-Z]+[0-9]+', cell_address)
        result = self.sheet_service.get(spreadsheetId=self.spreadsheet_id,
                                        ranges=[f'{self.sheet_name}!{cell_address}'],
                                        includeGridData=True,
                                        ).execute()
        time.sleep(1)

        return {
            'properties':   result['properties'],
            'columnFormat': result['sheets'][0]['data'][0]['columnMetadata'][0],
            'cellFormat':   result['sheets'][0]['data'][0]['rowData'][0]['values'][0],
        }

    def get_properties_many(self, range_start, range_end):  # todo: range_address instead
        assert re.fullmatch(r'[A-Z]+[0-9]+', range_start)
        assert re.fullmatch(r'[A-Z]+[0-9]+', range_end)
        result = self.sheet_service.get(spreadsheetId=self.spreadsheet_id,
                                        ranges=[f'{self.sheet_name}!{range_start}:{range_end}'],
                                        includeGridData=True,
                                        ).execute()
        time.sleep(1)

        return {
            'properties':    result['properties'],
            'columnFormats': result['sheets'][0]['data'][0]['columnMetadata'],
            'rowFormats':    result['sheets'][0]['data'][0]['rowData'],
        }

    def get_background_color(self, cell_address):
        _props = self.get_properties(cell_address)
        return color_float_to_hex(**_props['cellFormat']['effectiveFormat']['backgroundColor'])

    def get_background_colors(self, range_start, range_end):  # todo: range_address instead
        _props = self.get_properties_many(range_start, range_end)
        out = []
        for row in _props['rowFormats']:
            if not row.get('values'):
                out.append([])
                continue
            _row = []
            for cell in row['values']:
                if cell.get('effectiveFormat', {}).get('backgroundColor') is not None:
                    _row.append(color_float_to_hex(**cell['effectiveFormat']['backgroundColor']))
                else:
                    _row.append(None)
            out.append(_row)
        return out

    def get_horizontal_alignment(self, cell_address):
        _props = self.get_properties(cell_address)
        return _props['cellFormat']['effectiveFormat']['horizontalAlignment']

    def get_text_color(self, cell_address):
        _props = self.get_properties(cell_address)
        return color_float_to_hex(**_props['cellFormat']['effectiveFormat']['textFormat']['foregroundColor'])

    def get_value(self, cell_address):
        assert re.fullmatch(r'[A-Z]+[0-9]+', cell_address)
        result = self.sheet_service.values().get(spreadsheetId=self.spreadsheet_id,
                                                 range=f'{self.sheet_name}!{cell_address}',
                                                 ).execute()
        time.sleep(1)
        return result.get('values', [])[0][0]

    def get_values(self, range_start, range_end):  # todo: range_address instead
        assert re.fullmatch(r'[A-Z]+[0-9]+', range_start)
        assert re.fullmatch(r'[A-Z]+[0-9]+', range_end)
        result = self.sheet_service.values().get(spreadsheetId=self.spreadsheet_id,
                                                 range=f'{self.sheet_name}!{range_start}:{range_end}',
                                                 ).execute()
        time.sleep(1)
        return result.get('values', [])

    def set_background_color(self,
                             range_start: str,
                             range_end=None,  # todo: range_address instead
                             *,
                             color: Optional[str] = None,
                             ):
        if color is None:
            color = '#FFFFFF'

        body = {"requests": [{"repeatCell": {
            "fields": "userEnteredFormat.backgroundColor",
            "range":  self._get_sheet_range(range_start, range_end),
            "cell":   {"userEnteredFormat": {"backgroundColor": color_hex_to_float(color)}},
        }}]}
        time.sleep(1)
        return self.sheet_service.batchUpdate(spreadsheetId=self.spreadsheet_id, body=body).execute()

    def set_text_format(self,
                        range_start,
                        range_end=None,  # todo: range_address instead
                        *,
                        color: Optional[str] = None,
                        bold: Optional[bool] = None,
                        italic: Optional[bool] = None,
                        underline: Optional[bool] = None,
                        strikethrough: Optional[bool] = None,
                        font_size: Optional[Union[float, int]] = None,
                        ):

        body = {"requests": [{"repeatCell": {
            "fields": "userEnteredFormat.textFormat",
            "range":  self._get_sheet_range(range_start, range_end),
            "cell":   {"userEnteredFormat": {
                "textFormat": {"fontSize":        font_size,
                               "bold":            bold,
                               "italic":          italic,
                               "underline":       underline,
                               "strikethrough":   strikethrough,
                               "foregroundColor": None if color is None else color_hex_to_float(color),
                               }}},
        }}]}
        time.sleep(1)
        return self.sheet_service.batchUpdate(spreadsheetId=self.spreadsheet_id, body=body).execute()

    def set_horizontal_alignment(self,
                                 range_start,
                                 range_end=None,  # todo: range_address instead
                                 *,
                                 horizontal_alignment: Optional[str] = None,
                                 ):
        if horizontal_alignment is not None:
            if not isinstance(horizontal_alignment, str):
                raise TypeError(horizontal_alignment)
            if horizontal_alignment.casefold() not in {'left', 'center', 'right'}:  # american spelling only
                raise ValueError(horizontal_alignment)
        body = {"requests": [{"repeatCell": {
            "fields": "userEnteredFormat.horizontalAlignment",
            "range":  self._get_sheet_range(range_start, range_end),
            "cell":   {"userEnteredFormat": {"horizontalAlignment": horizontal_alignment}},
        }}]}
        time.sleep(1)
        return self.sheet_service.batchUpdate(spreadsheetId=self.spreadsheet_id, body=body).execute()

    def get_first_empty_row_after_existing_content(self, *, zero_index=False):
        result = self.sheet_service.values().append(
            spreadsheetId=self.spreadsheet_id,
            range=f'{self.sheet_name}',
            valueInputOption='USER_ENTERED',  # or 'RAW'
            body={'values': [[]]},
        ).execute()
        time.sleep(1)
        return parse_column_notation(result['updates']['updatedRange'].rpartition('!')[-1], zero_index=zero_index)[0]

    def append_values(self, values, after_end=True):
        """
        returns something like
        {'spreadsheetId': '1NeklzsZ_EZXz0W5eyPdRbZmGpNqIdAGJyIMVYO342oo',
         'updates':       {'spreadsheetId': '1NeklzsZ_EZXz0W5eyPdRbZmGpNqIdAGJyIMVYO342oo',
                           'updatedRange':  'Sheet6!A13',
                           'updatedRows':    1,
                           'updatedColumns': 1,
                           'updatedCells':   1,
                           }}
        """
        empty_row_idx = self.get_first_empty_row_after_existing_content() if after_end else 1
        result = self.sheet_service.values().append(
            spreadsheetId=self.spreadsheet_id,
            range=f'{self.sheet_name}!A{empty_row_idx}',
            valueInputOption='USER_ENTERED',  # or 'RAW'
            body={'values': values},
        ).execute()
        time.sleep(1)
        return result

    def set_values(self, range_start, range_end, values):  # todo: range_address instead
        result = self.sheet_service.values().update(
            spreadsheetId=self.spreadsheet_id,
            range=f'{self.sheet_name}!{range_start}:{range_end}',
            valueInputOption='USER_ENTERED',  # or 'RAW'
            body={'values': values},
        ).execute()
        time.sleep(1)
        return result

    def set_value(self, cell_address, value):
        assert isinstance(value, str)
        result = self.sheet_service.values().update(
            spreadsheetId=self.spreadsheet_id,
            range=f'{self.sheet_name}!{cell_address}',
            valueInputOption='USER_ENTERED',  # or 'RAW'
            body={'values': [[value]]},
        ).execute()
        time.sleep(1)
        return result


@dataclass
class SheetCache:
    table: List[List[str]]

    def __post_init__(self):
        max_row_len = max(len(row) for row in self.table)
        for row in self.table:
            while len(row) < max_row_len:
                row.append('')

    def __getitem__(self, item):
        row, column = parse_column_notation(item, zero_index=True)
        if row >= len(self.table):
            raise IndexError(row)
        if column >= len(self.table[row]):
            raise IndexError(column)
        return self.table[row][column]

    def get_values(self, range_start, range_end):
        row_start, col_start = parse_column_notation(range_start, zero_index=True)
        row_end, col_end = parse_column_notation(range_end, zero_index=True)
        return [row[col_start:col_end + 1] for row in self.table[row_start:row_end + 1]]


if __name__ == '__main__':
    # # https://docs.google.com/spreadsheets/d/1ahbAXvuamz2PB1COGx2dWjIV8BN75bqYL_KmgdHkWKk/edit#gid=1211096710
    # # sheet = Sheet('1ahbAXvuamz2PB1COGx2dWjIV8BN75bqYL_KmgdHkWKk', '...')
    #
    # # https://docs.google.com/spreadsheets/d/1Hx_oFmbRYRuek_eyVUyfz4_b9861mPhSBF1NHH9et70/edit#gid=1116371039
    # sheets = {  # copy, so I don't break anything
    #     'Blk 95A': Sheet('1Hx_oFmbRYRuek_eyVUyfz4_b9861mPhSBF1NHH9et70', 'Blk 95A'),
    #     'Blk 95B': Sheet('1Hx_oFmbRYRuek_eyVUyfz4_b9861mPhSBF1NHH9et70', 'Blk 95B'),
    #     'Blk 95C': Sheet('1Hx_oFmbRYRuek_eyVUyfz4_b9861mPhSBF1NHH9et70', 'Blk 95C'),
    #     'Blk 97A': Sheet('1Hx_oFmbRYRuek_eyVUyfz4_b9861mPhSBF1NHH9et70', 'Blk 97A'),
    #     'Blk 97B': Sheet('1Hx_oFmbRYRuek_eyVUyfz4_b9861mPhSBF1NHH9et70', 'Blk 97B'),
    #     'Blk 99A': Sheet('1Hx_oFmbRYRuek_eyVUyfz4_b9861mPhSBF1NHH9et70', 'Blk 99A'),
    #     'Blk 99B': Sheet('1Hx_oFmbRYRuek_eyVUyfz4_b9861mPhSBF1NHH9et70', 'Blk 99B'),
    # }
    #
    # tables = {block: dict() for block in sheets.keys()}
    # for block, sheet in sheets.items():
    #     level_dict = dict.fromkeys(range(2, 20))
    #     stack_dict = dict()
    #     header_row = None
    #     for i, row in enumerate(sheet.get_values('A1', f'A{sheet.get_first_empty_row_after_existing_content()}')):
    #         if not row:
    #             continue
    #         value = row[0]
    #         row_idx = i + 1
    #         if value.strip() == 'LEVEL/UNIT':
    #             header_row = row_idx
    #         if header_row and value.isdigit() and int(value) in level_dict:
    #             assert level_dict[int(value)] is None
    #             level_dict[int(value)] = row_idx
    #
    #     for j, value in enumerate(sheet.get_values(f'B{header_row}', f'Z{header_row}')[0]):
    #         col_idx = j + 2
    #         if not value.isdigit():
    #             continue
    #         stack_dict[int(value)] = col_idx
    #
    #     print(block)
    #     print(level_dict)
    #     print(stack_dict)
    #     for level, row_idx in level_dict.items():
    #         for stack, col_idx in stack_dict.items():
    #             tables[block][f'#{level:02d}-{stack}'] = build_column_notation(row_idx, col_idx)
    #     print(tables[block])

    # sheet = Sheet('1Hx_oFmbRYRuek_eyVUyfz4_b9861mPhSBF1NHH9et70', 'Blk 95A')  # copy
    # colors = sheet.get_background_colors('A15', 'C20')
    # pprint(colors)
    # pprint([[color_hex_to_name(cell) for cell in row] for row in colors])
    sheet = Sheet('1Hx_oFmbRYRuek_eyVUyfz4_b9861mPhSBF1NHH9et70', 'Sheet30')  # copy
    # sheet.set_sheet_dimensions(5,5)
    sheet.append_sheet_dimensions(5,2)
