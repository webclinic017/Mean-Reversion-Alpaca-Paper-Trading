import requests
import json
import alpaca_trade_api as tradeapi
import time
from alpaca_trade_api.rest import REST, TimeFrame, TimeFrameUnit

from config import *

API_KEY = "PKHFD2UWELHF95JACGKR"
SECRET_KEY = "WsrsxsVw14EwhNhpQCHfalh2j7mYZQKLAJVNKGiS"

BASE_URL = "https://paper-api.alpaca.markets"
ACCOUNT_URL = "{}/v2/account".format(BASE_URL)
ORDERS_URL = "{}/v2/orders".format(BASE_URL)

HEADERS = {'APCA-API-KEY-ID': API_KEY, 'APCA-API-SECRET-KEY': SECRET_KEY}

api = tradeapi.REST(
    'PKHFD2UWELHF95JACGKR',
    'WsrsxsVw14EwhNhpQCHfalh2j7mYZQKLAJVNKGiS',
    'https://paper-api.alpaca.markets', api_version='v2'
)

account = api.get_account()


def get_balance():

    if account.trading_blocked:
        print('Account is currently restricted from trading.')

    print('${} is available as buying power.'.format(account.buying_power))

    balance_change = float(account.equity) - float(account.last_equity)
    print(f'Today\'s portfolio balance change: ${balance_change}')


def get_assets():
    active_assets = api.list_assets(status='active')

    nasdaq_assets = [a for a in active_assets if a.exchange == 'NASDAQ']
    print(nasdaq_assets)


def get_account():
    r = requests.get(ACCOUNT_URL, headers=HEADERS)

    return json.loads(r.content)


def check_asset(symbol):
    data = {
        "symbol": symbol
    }

    asset = api.get_asset(symbol)
    if asset.tradable:
        print('We can trade ' + symbol + '.')
    else:
        print('We can not trade ' + symbol + '.')


def check_market(date):
    data = {
        "date": date
    }

    clock = api.get_clock()
    print('The market is {}'.format('open.' if clock.is_open else 'closed.'))

    calendar = api.get_calendar(start=date, end=date)[0]
    print('The market opened at {} and closed at {} on {}.'.format(
        calendar.open,
        calendar.open,
        date
    ))


def get_historical_data(symbol, type):
    data = {
        "symbol": symbol,
        "type": type,
    }

    barset = api.get_barset(symbol, type, limit=5)
    bars = barset[symbol]

    week_open = bars[0].o
    week_close = bars[-1].c
    percent_change = (week_close - week_open) / week_open * 100
    print(symbol + ' moved {}% over the last 5 days.'.format(percent_change))


def create_order(symbol, qty, side, type, time):
    data = {
        "symbol": symbol,
        "qty": qty,
        "side": side,
        "type": type,
        "time_in_force": time
    }

    r = requests.post(ORDERS_URL, json=data, headers=HEADERS)

    return json.loads(r.content)


def limit_order(symbol):
    data = {
        "symbol": symbol
    }

    create_order(symbol, 1, 'sell', 'market', 'day')
    print('Market order submitted.')

    symbol_bars = api.get_barset(symbol, 'minute', 1).df.iloc[0]
    symbol_price = symbol_bars[symbol]['close']

    api.submit_order(symbol, 1, 'sell', 'limit', 'day', symbol_price)
    print('Limit order submitted.')

    print('Waiting...')
    time.sleep(1)

    position = api.get_position(symbol)
    if int(position.qty) < 0:
        print(f'Short position open for {symbol}')


def get_positions(symbol):
    data = {
        "symbol": symbol
    }
    position = api.get_position(symbol)

    portfolio = api.list_positions()

    for position in portfolio:
        print("{} shares of {}".format(position.qty, position.symbol))


get_balance()
check_asset('AAPL')
check_market('2018-12-05')
get_historical_data('AAPL', 'day')
limit_order('AAPL')
get_positions('AAPL')

# Get list of assets
# print(get_assets())
