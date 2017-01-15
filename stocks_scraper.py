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

def __validate_response(response, tag):
    if not __is_valid_response(response):
        if 'error' in response:
            raise QueryError('YQL query failed with error: "%s".'
                             % response['error']['description'])
        raise QueryError('YQL response malformed.')
    elif (response['query']['results'] is None
          or tag not in response['query']['results']):
        raise NoResultsError('No results found.')
    return response['query']['results'][tag]

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

#fetch historical info for a stock ticker
def get_historical_info(symbol, from_dt=None, to_dt=None):
    """
    Historical data includes date, open, close, high, low, volume,
    and adjusted close.
    """

    if from_dt is None or to_dt is None:
        date_string = ''
    else:
        date_string = ('&a=%d&b=%d&c=%d&d=%d&e=%d&f=%d&g=d&ignore=.csv' %
                       (from_dt.month-1, from_dt.day, from_dt.year,
                        to_dt.month-1, to_dt.day, to_dt.year))

    yql = ('select * from csv where url="%s"'
           ' and columns="Date,Open,High,Low,Close,Volume,AdjClose"' %
           (HISTORICAL_URL + symbol + date_string))
    response = execute_yql_query(yql)
    results = __validate_response(response, 'row')
    # delete first row which contains column names
    del results[0]
    return results

#fetch RSS feed for the specifued symbol
def get_news_feed(symbol):
    feed_url = RSS_URL + symbol
    yql = ('select title, link, description, pubDate '
           'from rss where url="%s"' % feed_url)
    response = execute_yql_query(yql)
    return __validate_response(response, 'item')

#DRIVER
if __name__ == "__main__":
    if ''.join(str(e) for e in (sys.argv[1:])) == "":
        print 'WRONG INVOCATION OF SCRIPT'
        print 'GIVE A TICKER AS AN ARGUMENT. I AM AWARE OF:\n', get_stock_tickers()
        sys.exit(1)
    else:
        print ("""
        1. HISTORICAL INFO
        2. CURRENT INFO
        3. RSS FEED DATA
        """)

        ans = raw_input("What would you like to do? ")

        if ans=="1":
            print get_historical_info(''.join(str(e) for e in (sys.argv[1:])))
        elif ans=="2":
            print get_current_info(sys.argv[1:])
        elif ans=="3":
            print get_news_feed(''.join(str(e) for e in(sys.argv[1:])))
