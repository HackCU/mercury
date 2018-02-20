from __future__ import unicode_literals

import csv
import logging

import requests
from django.utils.encoding import force_str, force_text

logger = logging.getLogger(__name__)
gdocs_format = \
    'https://docs.google.com/spreadsheets/d/{key}/export?format=csv'

SHEETS_URL = \
    'https://docs.google.com/spreadsheets/d/{key}/edit?gid={gid}'

CACHE_KEY = 'django-sheets-{key}-{gid}'


class Sheet:
    def __init__(self, key, gid):
        if not key:
            raise RuntimeError('Sheet key not supplied')
        self.key = key
        self.gid = gid

    def __len__(self):
        return len(self.data)

    def __iter__(self):
        return iter(self.data)

    @property
    def lists(self):
        return self.data[0] if self.data else []

    def _rows(self):
        return self.data[1:] if len(self) > 1 else []

    def _fetch_sheet(self):
        try:
            gdocs_url = gdocs_format.format(key=self.key)
            if self.gid:
                gdocs_url += '&gid={}'.format(self.gid)
            response = requests.get(gdocs_url)
            response.raise_for_status()
            return force_str(response.content)
        except requests.HTTPError as exp:
            logger.error('Error fetching spreadsheet: %s' % exp)
            return force_str('')

    def fetch_sheet(self):
        return self._fetch_sheet()

    @property
    def data(self):
        sheet = self.fetch_sheet()
        reader = csv.reader(
            sheet.splitlines(),
            delimiter=str(','),
            quotechar=str('"'),
            quoting=csv.QUOTE_MINIMAL,
        )
        return [[force_text(cell) for cell in row] for row in reader]

    def get_list(self, title):
        if title not in self.lists:
            return []

        index = self.lists.index(title)
        return [row[index] for row in self._rows()]
