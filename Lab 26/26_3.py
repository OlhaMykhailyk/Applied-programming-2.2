import re
import html.parser
from urllib.request import urlopen
from urllib.error import HTTPError
from datetime import datetime
from openpyxl import Workbook


class MeteoRegex:
    def __init__(self, city):
        self.city = city
        self._data = []
        url = 'https://www.meteoprog.ua/ru/weather/{}/'.format(city)

        try:
            request = urlopen(url)
            html = request.read().decode('utf-8','ignore')

            min_t = re.findall(r'class="min">(-?\d+)', html)
            max_t = re.findall(r'class="max">\+?(-?\d+)', html)

            for i in range(5):
                self._data.append((min_t[i], max_t[i]))

        except HTTPError as e:
            print(e)

    @property
    def forecast(self):
        return self._data


class MeteoParser(html.parser.HTMLParser):

    def __init__(self):
        html.parser.HTMLParser.__init__(self)
        self.mins = []
        self.maxs = []
        self._min = False
        self._max = False

    def handle_starttag(self, tag, attrs):
        for a in attrs:
            if a[0]=='class' and 'min' in a[1]:
                self._min = True
            if a[0]=='class' and 'max' in a[1]:
                self._max = True

    def handle_endtag(self, tag):
        self._min = False
        self._max = False

    def handle_data(self, data):
        if self._min:
            t = data.strip()
            if t:
                self.mins.append(t)

        if self._max:
            t = data.strip()
            if t:
                self.maxs.append(t)


class MeteoHTML:

    def __init__(self, city):
        self.city = city
        self._data = []

        url = 'https://www.meteoprog.ua/ru/weather/{}/'.format(city)

        try:
            request = urlopen(url)
            html = request.read().decode('utf-8','ignore')

            parser = MeteoParser()
            parser.feed(html)

            for i in range(5):
                self._data.append((parser.mins[i],parser.maxs[i]))

        except HTTPError as e:
            print(e)

    @property
    def forecast(self):
        return self._data


class ExcelWriter:

    def __init__(self, filename):
        self.filename = filename

    def write(self,data):

        wb = Workbook()
        ws = wb.active

        ws.append(['Date','Day1 min','Day1 max',
                   'Day2 min','Day2 max',
                   'Day3 min','Day3 max',
                   'Day4 min','Day4 max',
                   'Day5 min','Day5 max'])

        row = [datetime.now().strftime('%Y-%m-%d')]

        for d in data:
            row.append(d[0])
            row.append(d[1])

        ws.append(row)

        wb.save(self.filename)


if __name__ == '__main__':

    city = input('City: ')

    mr = MeteoRegex(city)
    mh = MeteoHTML(city)

    ew = ExcelWriter('weather.xlsx')

    ew.write(mr.forecast)

    print(mr.forecast)
    print(mh.forecast)