import datetime
import json
from pathlib import Path

import pandas as pd
import requests
from bs4 import BeautifulSoup

from availability.google_sheets_test import Sheet
from availability.google_sheets_test import build_column_notation

backups_dir = Path('backups')

if __name__ == '__main__':

    # load unit metadata
    with open('unit-metadata.json', 'rb') as f:
        unit_metadata = json.load(f)

    # load json
    prev_file = sorted(backups_dir.glob('*-*-*--*-*-*.json'))[-2]
    curr_file = sorted(backups_dir.glob('*-*-*--*-*-*.json'))[-1]
    with prev_file.open('rb') as f:
        prev_data = json.load(f)
    with curr_file.open('rb') as f:
        curr_data = json.load(f)
    removed_ids = [int(unit_id) for unit_id in prev_data['availabilitySet']
                   if unit_id not in curr_data['availabilitySet']]

    r = requests.get('https://resources.homes.hdb.gov.sg/nf/2021-05/bto/unit_xml/'
                     'UNIT_2021-05_BTO_R0xfTjFDMTNfMTYxOTUwMjc4NDU1Ng.xml',
                     verify=False)
    soup = BeautifulSoup(r.content, 'lxml-xml')

    rows = []
    for block in soup.find_all('block'):
        block_number = block.find('block-number')
        for flat_type in block.find_all('flat-type'):
            _type = flat_type.find('type')
            for level in flat_type.find_all('level'):
                level_number = level.find('level-number')
                for unit in level.find_all('unit'):
                    unit_id = unit.find('unit-id')
                    unit_number = unit.find('unit-number')
                    area_sqm = unit.find('area')
                    price = unit.find('price')

                    unit_tag = unit_metadata.get(f'#{level_number.text}-{unit_number.text}', '')

                    rows.append([block_number.text,
                                 _type.text,
                                 f'#{level_number.text}',
                                 int(level_number.text.lstrip('0')),
                                 int(unit_id.text),
                                 int(unit_number.text),
                                 int(area_sqm.text),
                                 int(price.text),
                                 unit_tag,
                                 False,  # default availability
                                 ])

    headers = ['block',
               'flat_type',
               'level_str',
               'level_number',
               'unit_id',
               'stack',
               'area_sqm',
               'price',
               'tag',
               'available',
               ]
    df = pd.DataFrame(rows, columns=headers)
    df_removed = df[df['unit_id'].apply(lambda x: x in removed_ids)]

    sheet = Sheet('1Hx_oFmbRYRuek_eyVUyfz4_b9861mPhSBF1NHH9et70', 'Units taken by date')  # copy
    next_row = sheet.get_first_empty_row_after_existing_content()

    date_str = (datetime.datetime.strptime(curr_file.stem, '%Y-%m-%d--%H-%M-%S')
                - datetime.timedelta(hours=12)).strftime('%d/%m/%Y')
    print(date_str + '\t' + 'Public queue')
    next_row += 1
    sheet.set_values(f'A{next_row}', f'B{next_row}', [[date_str, 'Public queue']])
    sheet.set_text_format(f'A{next_row}', f'B{next_row}', bold=True)
    sheet.set_horizontal_alignment(f'A{next_row}', horizontal_alignment='left')
    sheet.set_background_color(f'A{next_row}', f'B{next_row}', color='#d9d9d9')
    next_row += 1

    n_2rm = str(len(df_removed[df_removed['flat_type'].str.contains('2-Room')]))

    print('2-room total:\t' + n_2rm)
    sheet.set_values(f'A{next_row}', f'B{next_row}', [['2-room total:', n_2rm]])
    sheet.set_text_format(f'A{next_row}', f'B{next_row}', bold=True)
    next_row += 1
    for i, row in df_removed[df_removed['flat_type'].str.contains('2-Room')].iterrows():
        print('Blk ' + str(row['block']) + '\t' + row['level_str'] + '-' + str(row['stack']))
        sheet.set_values(f'A{next_row}', f'B{next_row}', [['Blk ' + str(row['block']),
                                                           row['level_str'] + '-' + str(row['stack'])]])
        next_row += 1
    print()
    next_row += 1

    n_3rm = str(len(df_removed[df_removed['flat_type'].str.contains('3-Room')]))
    print('3-room total:\t' + n_3rm)
    sheet.set_values(f'A{next_row}', f'B{next_row}', [['3-room total:', n_3rm]])
    sheet.set_text_format(f'A{next_row}', f'B{next_row}', bold=True)
    next_row += 1
    for i, row in df_removed[df_removed['flat_type'].str.contains('3-Room')].iterrows():
        print('Blk ' + str(row['block']) + '\t' + row['level_str'] + '-' + str(row['stack']))
        sheet.set_values(f'A{next_row}', f'B{next_row}', [['Blk ' + str(row['block']),
                                                           row['level_str'] + '-' + str(row['stack'])]])
        next_row += 1
    print()
    next_row += 1

    n_4rm = str(len(df_removed[df_removed['flat_type'].str.contains('4-Room')]))
    print('4-room total:\t' + n_4rm)
    sheet.set_values(f'A{next_row}', f'B{next_row}', [['4-room total:', n_4rm]])
    sheet.set_text_format(f'A{next_row}', f'B{next_row}', bold=True)
    next_row += 1
    for i, row in df_removed[df_removed['flat_type'].str.contains('4-Room')].iterrows():
        print('Blk ' + str(row['block']) + '\t' + row['level_str'] + '-' + str(row['stack']))
        sheet.set_values(f'A{next_row}', f'B{next_row}', [['Blk ' + str(row['block']),
                                                           row['level_str'] + '-' + str(row['stack'])]])
        next_row += 1

    sheets = {  # copy, so I don't break anything
        'Blk 95A': Sheet('1Hx_oFmbRYRuek_eyVUyfz4_b9861mPhSBF1NHH9et70', 'Blk 95A'),
        'Blk 95B': Sheet('1Hx_oFmbRYRuek_eyVUyfz4_b9861mPhSBF1NHH9et70', 'Blk 95B'),
        'Blk 95C': Sheet('1Hx_oFmbRYRuek_eyVUyfz4_b9861mPhSBF1NHH9et70', 'Blk 95C'),
        'Blk 97A': Sheet('1Hx_oFmbRYRuek_eyVUyfz4_b9861mPhSBF1NHH9et70', 'Blk 97A'),
        'Blk 97B': Sheet('1Hx_oFmbRYRuek_eyVUyfz4_b9861mPhSBF1NHH9et70', 'Blk 97B'),
        'Blk 99A': Sheet('1Hx_oFmbRYRuek_eyVUyfz4_b9861mPhSBF1NHH9et70', 'Blk 99A'),
        'Blk 99B': Sheet('1Hx_oFmbRYRuek_eyVUyfz4_b9861mPhSBF1NHH9et70', 'Blk 99B'),
    }

    tables = {block: dict() for block in sheets.keys()}
    for block, sheet in sheets.items():
        level_dict = dict.fromkeys(range(2, 20))
        stack_dict = dict()
        header_row = None
        for i, row in enumerate(sheet.get_values('A1', f'A{sheet.get_first_empty_row_after_existing_content()}')):
            if not row:
                continue
            value = row[0]
            row_idx = i + 1
            if value.strip() == 'LEVEL/UNIT':
                header_row = row_idx
            if header_row and value.isdigit() and int(value) in level_dict:
                assert level_dict[int(value)] is None
                level_dict[int(value)] = row_idx

        for j, value in enumerate(sheet.get_values(f'B{header_row}', f'Z{header_row}')[0]):
            col_idx = j + 2
            if not value.isdigit():
                continue
            stack_dict[int(value)] = col_idx

        print(block)
        print(level_dict)
        print(stack_dict)
        for level, row_idx in level_dict.items():
            for stack, col_idx in stack_dict.items():
                tables[block][f'#{level:02d}-{stack}'] = build_column_notation(row_idx, col_idx)
        print(tables[block])

    for i, row in df_removed.iterrows():
        block = 'Blk ' + str(row['block'])
        unit = row['level_str'] + '-' + str(row['stack'])
        cell_address = tables[block][unit]
        print('gray', block, unit, cell_address)
        sheets[block].set_background_color(cell_address, color='#999')
