import datetime
import json
import re
from pathlib import Path

import pandas as pd
import requests
import tabulate
from bs4 import BeautifulSoup

out = Path('parsed_xml2_downloads')

if __name__ == '__main__':
    directory = Path('hdb_downloads')
    for path in directory.glob('2024-02_BTO_*.xml'):
        soup = BeautifulSoup(path.read_bytes(), 'lxml-xml')
        town = soup.find('town').text.replace('/', '+')
        project_name = soup.find('project-name').text
        print(f'{town} ({project_name})')

        stack = [soup]
        while stack:
            elem = stack.pop(-1)
            children = elem.findChildren()
            if children:
                stack.extend(children)
                continue

            if re.fullmatch(r'[0-9]{4}-[0-9]{2}/.+\.[a-z]{2,5}', elem.text):
                r = requests.get(f'https://resources.homes.hdb.gov.sg/nf/{elem.text}', verify=False)
                if r.status_code == 200:
                    out_path = out / elem.text
                    out_path.parent.mkdir(parents=True, exist_ok=True)
                    out_path.write_bytes(r.content)
