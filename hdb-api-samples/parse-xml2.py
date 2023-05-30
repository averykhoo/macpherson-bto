import datetime
import json
from pathlib import Path

import pandas as pd
import requests
import tabulate
from bs4 import BeautifulSoup

if __name__ == '__main__':
    directory = Path('hdb_downloads')
    for path in directory.glob('2023-05_BTO_*.xml'):
        soup = BeautifulSoup(path.read_bytes(), 'lxml-xml')
        town = soup.find('town').text.replace('/','+')
        project_name = soup.find('project-name').text
        print(f'{town} ({project_name})')

