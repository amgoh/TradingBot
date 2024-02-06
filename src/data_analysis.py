import os
from socket import create_connection
import time
from threading import Thread
import asyncio
from dotenv import load_dotenv
import pickle
import stock_order as stocks
from alpaca.trading.client import TradingClient
from alpaca.trading.stream import TradingStream
from alpaca.data.live.stock import StockDataStream
from alpaca.data.historical.stock import StockHistoricalDataClient
from alpaca.data.requests import StockLatestQuoteRequest
from alpaca.data.enums import DataFeed
from alpaca.data.models.bars import *
from alpaca.data.models.quotes import *
import simplejson as json
import pprint
from datetime import datetime, timedelta

load_dotenv()
API_KEY = os.getenv("API-KEY")
SECRET_KEY = os.getenv("SECRET-KEY")


url = 'wss://stream.data.alpaca.markets/v2/iex'
web_socket = create_connection(url)
print(json.loads(web_socket.recv()))

data_stream = {}

def algo():

    start = datetime.utcnow()
    while datetime.utcnow() - start < timedelta(seconds= 5*60*60):
        data : StockLatestQuoteRequest
        data_stream[datetime.utcnow()] = data.bid_price

    top_half_bump = (data_stream[start + timedelta(seconds= 3.5*60*60)] - data_stream[start + timedelta(seconds= 1.7*60*60)])/2
    bot_half_bump = (data_stream[start + timedelta(seconds= 1.7*60*60)] - data_stream[start])/2
    run = (data_stream[start + timedelta(seconds= 5*60*60)] - data_stream[start + timedelta(seconds= 3.5*60*60)])/2
    
    if top_half_bump == bot_half_bump:
        if run >= 1.5*top_half_bump:
            bump_run(True)
        bump_run(False)


def bump_run(val):
    stocks.place_order()


'''
recent_data_bid = {}
recent_data_ask = {}
owned_stocks = []

dataStream = StockDataStream(API_KEY, SECRET_KEY, feed=DataFeed.IEX)

def run():
    #Initialize trading client, data client, and account
    client = TradingClient(API_KEY, SECRET_KEY, paper=True)
    dataClient = StockHistoricalDataClient(API_KEY, SECRET_KEY)
    account = client.get_account()
    #List of all positions at bot initialization
    positions = client.get_all_positions()
    for s in positions:
        #Add stock symbol to a list used to re-check stocks later
        owned_stocks.append(s.symbol)
        
        #Start listening for quote data from owned stocks
        dataStream.subscribe_quotes(data_handler, s.symbol)

async def data_handler(data: Quote):
    if(data.bid_price != 0 and data.ask_price != 0):
        recent_data_bid[data.symbol] = data.bid_price
        recent_data_ask[data.symbol] = data.ask_price
'''