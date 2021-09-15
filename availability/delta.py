import datetime
import json
from pathlib import Path

import pandas as pd
import requests
from bs4 import BeautifulSoup

from availability.google_sheets_test import Sheet

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
