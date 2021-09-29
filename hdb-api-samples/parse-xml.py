import datetime
import json
from pathlib import Path

import pandas as pd
import requests
import tabulate
from bs4 import BeautifulSoup

if __name__ == '__main__':
    directory = Path('hdb_downloads')
    for path in directory.glob('UNIT_2021-08_BTO_*.xml'):
        soup = BeautifulSoup(path.read_bytes(), 'lxml-xml')
        town = soup.find('town').text.replace('/','+')
        project_name = soup.find('project-name').text
        print(f'{town} ({project_name})')

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

                        rows.append([block_number.text,
                                     _type.text,
                                     f'#{level_number.text}',
                                     int(level_number.text.lstrip('0')),
                                     unit_id.text,
                                     int(unit_number.text),
                                     int(area_sqm.text),
                                     int(price.text),
                                     ])

        headers = ['block',
                   'flat_type',
                   'level_str',
                   'level_number',
                   'unit_id',
                   'stack',
                   'area_sqm',
                   'price',
                   ]
        df = pd.DataFrame(rows, columns=headers)
        df.to_excel(f'{town} ({project_name}).xlsx', index=False)
