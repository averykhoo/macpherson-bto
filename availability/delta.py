import csv
import datetime
import json
from pathlib import Path

import pandas as pd
import requests
from bs4 import BeautifulSoup
from tabulate import tabulate

from availability.google_sheets_test import Sheet
from availability.google_sheets_test import SheetCache
from availability.google_sheets_test import build_column_notation
from availability.google_sheets_test import color_hex_to_name
from availability.google_sheets_test import parse_column_notation

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

    workbook_id = '1ahbAXvuamz2PB1COGx2dWjIV8BN75bqYL_KmgdHkWKk'  # original
    # workbook_id = '1Hx_oFmbRYRuek_eyVUyfz4_b9861mPhSBF1NHH9et70'  # copy, so I don't break anything

    read_only = 0  # True

    # # # update list of taken units

    sheet = Sheet(workbook_id, 'Units taken by date')
    next_row = sheet.get_first_empty_row_after_existing_content()
    cache = SheetCache(sheet.get_values('A1', f'Z{next_row}'))

    date_str_1 = (datetime.datetime.strptime(curr_file.stem, '%Y-%m-%d--%H-%M-%S')
                  - datetime.timedelta(hours=12)).strftime('%d/%m/%Y')
    date_str_2 = (datetime.datetime.strptime(curr_file.stem, '%Y-%m-%d--%H-%M-%S')
                  - datetime.timedelta(hours=12)).strftime('%m/%d/%Y')
    date_str_3 = (datetime.datetime.strptime(curr_file.stem, '%Y-%m-%d--%H-%M-%S')
                  - datetime.timedelta(hours=12)).strftime('%m/%d/%Y').replace('/0', '/')
    date_already_exists = any(row[0].strip() in {date_str_1, date_str_2, date_str_3} for row in cache.table[-50:])
    if not read_only and date_already_exists:
        print('already added data, not writing to sheet')

    original_row = next_row
    print(date_str_1 + '\t' + 'Public queue')
    next_row += 1
    if not read_only and not date_already_exists:
        current_time = datetime.datetime.now().strftime('%I:%M %p')
        # sheet.set_values(f'A{next_row}', f'C{next_row}', [[date_str_1, 'Public queue', f'updated at {current_time}']])
        sheet.set_values(f'A{next_row}', f'B{next_row}', [[date_str_1, 'Public queue']])
        sheet.set_text_format(f'A{next_row}', f'B{next_row}', bold=True)
        sheet.set_horizontal_alignment(f'A{next_row}', horizontal_alignment='left')
        sheet.set_background_color(f'A{next_row}', f'B{next_row}', color='#d9d9d9')
        next_row += 1

    n_2rm = str(len(df_removed[df_removed['flat_type'].str.contains('2-Room')]))

    print('2-room total:\t' + n_2rm)
    if not read_only and not date_already_exists:
        sheet.set_values(f'A{next_row}', f'B{next_row}', [['2-room total:', n_2rm]])
        sheet.set_text_format(f'A{next_row}', f'B{next_row}', bold=True)
        next_row += 1
    for i, row in df_removed[df_removed['flat_type'].str.contains('2-Room')].sort_values(
            by=['block', 'level_str', 'stack']).iterrows():
        print('BLK ' + str(row['block']) + '\t' + row['level_str'] + '-' + str(row['stack']))
        if not read_only and not date_already_exists:
            sheet.set_values(f'A{next_row}', f'B{next_row}',
                             [['BLK ' + str(row['block']), row['level_str'] + '-' + str(row['stack'])]])
            next_row += 1
    print()
    next_row += 1

    n_3rm = str(len(df_removed[df_removed['flat_type'].str.contains('3-Room')]))
    print('3-room total:\t' + n_3rm)
    if not read_only and not date_already_exists:
        sheet.set_values(f'A{next_row}', f'B{next_row}', [['3-room total:', n_3rm]])
        sheet.set_text_format(f'A{next_row}', f'B{next_row}', bold=True)
        next_row += 1
    for i, row in df_removed[df_removed['flat_type'].str.contains('3-Room')].sort_values(
            by=['block', 'level_str', 'stack']).iterrows():
        print('BLK ' + str(row['block']) + '\t' + row['level_str'] + '-' + str(row['stack']))
        if not read_only and not date_already_exists:
            sheet.set_values(f'A{next_row}', f'B{next_row}',
                             [['BLK ' + str(row['block']), row['level_str'] + '-' + str(row['stack'])]])
            next_row += 1
    print()
    next_row += 1

    n_4rm = str(len(df_removed[df_removed['flat_type'].str.contains('4-Room')]))
    print('4-room total:\t' + n_4rm)
    if not read_only and not date_already_exists:
        sheet.set_values(f'A{next_row}', f'B{next_row}', [['4-room total:', n_4rm]])
        sheet.set_text_format(f'A{next_row}', f'B{next_row}', bold=True)
        next_row += 1
    for i, row in df_removed[df_removed['flat_type'].str.contains('4-Room')].sort_values(
            by=['block', 'stack', 'level_str']).iterrows():
        print('BLK ' + str(row['block']) + '\t' + row['level_str'] + '-' + str(row['stack']))
        if not read_only and not date_already_exists:
            sheet.set_values(f'A{next_row}', f'B{next_row}',
                             [['BLK ' + str(row['block']), row['level_str'] + '-' + str(row['stack'])]])
            next_row += 1

    # append so we don't hit the end
    sheet_rows, _ = sheet.get_sheet_dimensions()
    next_row = sheet.get_first_empty_row_after_existing_content()
    if not read_only and sheet_rows - next_row < 100:
        print(f'extending sheet by {next_row + 100 - sheet_rows} rows')
        sheet.append_sheet_dimensions(next_row + 100 - sheet_rows, 0)

    # # # color the taken units gray

    sheets = {
        'Blk 95A': Sheet(workbook_id, 'Blk 95A'),
        'Blk 95B': Sheet(workbook_id, 'Blk 95B'),
        'Blk 95C': Sheet(workbook_id, 'Blk 95C'),
        'Blk 97A': Sheet(workbook_id, 'Blk 97A'),
        'Blk 97B': Sheet(workbook_id, 'Blk 97B'),
        'Blk 99A': Sheet(workbook_id, 'Blk 99A'),
        'Blk 99B': Sheet(workbook_id, 'Blk 99B'),
    }

    sheet_values = dict()
    sheet_colors = dict()
    for block, sheet in sheets.items():
        print(f'caching {block}...')
        last_row = sheet.get_first_empty_row_after_existing_content()
        sheet_values[block] = SheetCache(sheet.get_values('A1', f'Z{last_row}'))
        sheet_colors[block] = SheetCache(sheet.get_background_colors('A1', f'Z{last_row}'))
        print(tabulate([row for row in sheet_values[block].table if any(row)]))
        print(tabulate([row for row in sheet_colors[block].table if any(row)]))
        print(tabulate([[color_hex_to_name(cell) if cell else None for cell in row]
                        for row in sheet_colors[block].table if any(row)]))

    tables = {block: dict() for block in sheets.keys()}
    for block, sheet in sheets.items():
        # last_row = sheet.get_first_empty_row_after_existing_content()
        last_row = len(sheet_values[block].table)
        level_dict = dict.fromkeys(range(2, 20))
        stack_dict = dict()
        header_row = None
        for i, row in enumerate(sheet_values[block].get_values('A1', f'A{last_row}')):
            if not row:
                continue
            value = row[0]
            row_idx = i + 1
            if value.strip() == 'LEVEL/UNIT':
                header_row = row_idx
            if header_row and value.isdigit() and int(value) in level_dict:
                assert level_dict[int(value)] is None
                level_dict[int(value)] = row_idx

        for j, value in enumerate(sheet_values[block].get_values(f'B{header_row}', f'Z{header_row}')[0]):
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

        # # run once: fix formatting
        # top_left = build_column_notation(min(level_dict.values()) - 1, min(stack_dict.values()) - 1)
        # bottom_right = build_column_notation(max(level_dict.values()), max(stack_dict.values()) + 1)
        # print(top_left, bottom_right)
        # if not read_only:
        #     sheets[block].set_text_format(top_left, bottom_right)
        #     sheets[block].set_horizontal_alignment(top_left, bottom_right, horizontal_alignment='center')

    df = pd.read_csv('macpherson-prices.csv')
    for i, row in df[~df['available']].iterrows():
        block = 'Blk ' + str(row['block'])
        unit = row['level_str'] + '-' + str(row['stack'])
        cell_address = tables[block][unit]
        if sheet_colors[block][cell_address] != '#999999':
            print(block, unit, cell_address, color_hex_to_name(sheet_colors[block][cell_address]), 'to gray')
            if not read_only:
                sheets[block].set_background_color(cell_address, color='#999')

    # # run once: fix background colors
    # size_color = {38: '#F4CCCC',
    #               48: '#EA9999',
    #               69: '#B6D7A8',  # '#93C47D',
    #               93: '#FFD966',  # '#F1C232',
    #               }
    # for i, row in df[df['available']].iterrows():
    #     block = 'Blk ' + str(row['block'])
    #     unit = row['level_str'] + '-' + str(row['stack'])
    #     cell_address = tables[block][unit]
    #     if sheet_colors[block][cell_address] != size_color[row['area_sqm']]:
    #         print(block, unit, cell_address,
    #               color_hex_to_name(sheet_colors[block][cell_address]), sheet_colors[block][cell_address],
    #               'to',
    #               color_hex_to_name(size_color[row['area_sqm']]), size_color[row['area_sqm']])
    #         if not read_only:
    #             sheets[block].set_background_color(cell_address, color=size_color[row['area_sqm']])

    # # # update the remaining number of units

    # hardcode where to insert the remaining units because too lazy to parse
    remaining_count_locations = {
        ('Blk 95A', '2-room'): 'A29',
        ('Blk 95A', '3-room'): 'F29',
        ('Blk 95A', '4-room'): 'K29',
        ('Blk 95B', '2-room'): 'A30',
        ('Blk 95B', '3-room'): 'F30',
        ('Blk 95B', '4-room'): 'K30',
        ('Blk 95C', '4-room'): 'B27',
        ('Blk 97A', '4-room'): 'B28',
        ('Blk 97B', '4-room'): 'B27',
        ('Blk 99A', '4-room'): 'B28',
        ('Blk 99B', '4-room'): 'B27',
    }

    remaining_counts = dict()
    with open('macpherson-ethnic-quota.csv', encoding='utf8') as f:
        c = csv.reader(f)
        headers = next(c)
        for block, flat_type, chinese, malay, indian, remaining, total in c:
            remaining_counts[(f'Blk {block}', flat_type[:6])] = (chinese, malay, indian, remaining, total)

    for (sheet_name, room_type), cell_address in remaining_count_locations.items():
        print(sheet_name, room_type, cell_address)
        assert sheets[sheet_name].get_value(cell_address) == room_type

    for (sheet_name, room_type), cell_address in remaining_count_locations.items():
        print(f'checking {sheet_name} ({room_type}) remaining values')
        row, col = parse_column_notation(cell_address)
        total_cell = build_column_notation(row + 2, col + 3)
        total_remaining_cell = build_column_notation(row + 2, col + 1)
        malay_remaining_cell = build_column_notation(row + 6, col + 1)
        chinese_remaining_cell = build_column_notation(row + 7, col + 1)
        indian_remaining_cell = build_column_notation(row + 8, col + 1)

        chinese, malay, indian, remaining, total = remaining_counts[(sheet_name, room_type)]

        if sheet_values[sheet_name][total_cell] != total:
            print(f'updating total={total}')
            if not read_only:
                sheets[sheet_name].set_value(total_cell, total)

        if sheet_values[sheet_name][total_remaining_cell] != remaining:
            print(f'updating remaining={remaining}')
            if not read_only:
                sheets[sheet_name].set_value(total_remaining_cell, remaining)

        if sheet_values[sheet_name][malay_remaining_cell] != malay:
            print(f'updating malay={malay}')
            if not read_only:
                sheets[sheet_name].set_value(malay_remaining_cell, malay)

        if sheet_values[sheet_name][chinese_remaining_cell] != chinese:
            print(f'updating chinese={chinese}')
            if not read_only:
                sheets[sheet_name].set_value(chinese_remaining_cell, chinese)

        if sheet_values[sheet_name][indian_remaining_cell] != indian:
            print(f'updating indian={indian}')
            if not read_only:
                sheets[sheet_name].set_value(indian_remaining_cell, indian)
