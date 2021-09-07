import datetime
import json
from pathlib import Path

import pandas as pd
import requests
from bs4 import BeautifulSoup

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

    print((datetime.datetime.strptime(curr_file.stem, '%Y-%m-%d--%H-%M-%S') - datetime.timedelta(hours=12))
          .strftime('%d/%m/%Y') + '\t' + 'Public queue')
    print('2-Room total:\t' + str(len(df_removed[df_removed['flat_type'].str.contains('2-Room')])))
    for i, row in df_removed[df_removed['flat_type'].str.contains('2-Room')].iterrows():
        print('Blk ' + str(row['block']) + '\t' + row['level_str'] + '-' + str(row['stack']))
    print()
    print('3-Room total:\t' + str(len(df_removed[df_removed['flat_type'].str.contains('3-Room')])))
    for i, row in df_removed[df_removed['flat_type'].str.contains('3-Room')].iterrows():
        print('Blk ' + str(row['block']) + '\t' + row['level_str'] + '-' + str(row['stack']))
    print()
    print('4-Room total:\t' + str(len(df_removed[df_removed['flat_type'].str.contains('4-Room')])))
    for i, row in df_removed[df_removed['flat_type'].str.contains('4-Room')].iterrows():
        print('Blk ' + str(row['block']) + '\t' + row['level_str'] + '-' + str(row['stack']))
