#!/usr/bin/env python
import urllib
import urllib2
from bs4 import BeautifulSoup


def get_stock_tickers():
    req = urllib2.Request(
        'http://en.wikipedia.org/wiki/List_of_S%26P_500_companies')
    page = urllib2.urlopen(req)
    soup = BeautifulSoup(page, 'html.parser')
    table = soup.find('table', {'class': 'wikitable sortable'})
    tickers = []
    for row in table.findAll('tr'):
        col = row.findAll('td')
        if len(col) > 0:
            tickers.append(str(col[0].string.strip()))
    tickers.sort()
    return tickers
