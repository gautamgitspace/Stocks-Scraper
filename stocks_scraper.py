#!/usr/bin/env python
import urllib
import sys
import httplib
import urllib2
import json
from bs4 import BeautifulSoup

PUBLIC_API_URL = 'http://query.yahooapis.com/v1/public/yql'
DATATABLES_URL = 'store://datatables.org/alltableswithkeys'
HISTORICAL_URL = 'http://ichart.finance.yahoo.com/table.csv?s='
RSS_URL = 'http://finance.yahoo.com/rss/headline?s='
FINANCE_TABLES = {'quotes': 'yahoo.finance.quotes',
                  'options': 'yahoo.finance.options',
                  'quoteslist': 'yahoo.finance.quoteslist',
                  'sectors': 'yahoo.finance.sectors',
                  'industry': 'yahoo.finance.industry'}

class QueryError(Exception):
    pass

class NoResultsError(Exception):
    pass

def __format_symbol_list(symbols):
    return ",".join(["\"" + symbol + "\"" for symbol in symbols])

def __is_valid_response(response):
    return ('query' in response
            and 'results' in response['query']
            and 'error' not in response)
            
#fetch all available stock tickers
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

#fetch info of latest stock data for a ticker
def get_current_info(symbol_list, columns='*'):
    columns = ','.join(columns)
    symbols = __format_symbol_list(symbol_list)

    yql = ('select %s from %s where symbol in (%s)'
           % (columns, FINANCE_TABLES['quotes'], symbols))
    response = execute_yql_query(yql)
    return __validate_response(response, 'quote')
