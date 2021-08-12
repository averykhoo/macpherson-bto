import datetime
import json
from pathlib import Path

import pandas as pd
import requests
import tabulate
from bs4 import BeautifulSoup

backups_dir = Path('backups')
json_path = Path('getSelectionProjectAvailabilityAndEthnic.json')

if __name__ == '__main__':

    # load unit metadata
    with open('unit-metadata.json', 'rb') as f:
        unit_metadata = json.load(f)

    # load json
    with json_path.open('rb') as f:
        availability_json = json.load(f)
    prev_file = sorted(backups_dir.glob('*.json'))[-1]
    with prev_file.open('rb') as f:
        if json.load(f) != availability_json:
            new_path = backups_dir / f'{datetime.datetime.now().strftime("%Y-%m-%d--%H-%M-%S")}.json'
            with new_path.open('w', encoding='utf8') as f2:
                json.dump(availability_json, f2, indent=4)

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

    with open('getSelectionProjectAvailabilityAndEthnic.json', 'rb') as f:
        for unit_id in json.load(f)['availabilitySet']:
            df.loc[df['unit_id'] == int(unit_id), 'available'] = True

    print(tabulate.tabulate(df, headers=df.columns))
    df.to_csv('macpherson-prices.csv', index=False)

    rows_2 = []
    with open('getSelectionProjectAvailabilityAndEthnic.json', 'rb') as f:
        for block_data in json.load(f)['projectBlockFlatTypeInfoMap'].values():
            for unit_data in block_data.values():
                unit_data['remaining'] = df[(df['block'] == unit_data['block']) &
                                            (df['flat_type'].str.casefold() == unit_data['flatType'].casefold())
                                            ]['available'].sum()
                unit_data['total'] = len(df[(df['block'] == unit_data['block']) &
                                            (df['flat_type'].str.casefold() == unit_data['flatType'].casefold())
                                            ])
                rows_2.append(unit_data)

    df2 = pd.DataFrame(rows_2)
    df2.sort_values(by=['block', 'flatType'], inplace=True)
    df2.reset_index(drop=True, inplace=True)
    df2.rename(columns={'flatType': 'flat_type'}, inplace=True)

    print(tabulate.tabulate(df2, headers=df2.columns))
    df2.to_csv('macpherson-ethnic-quota.csv', index=False)
