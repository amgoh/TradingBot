import os
import time
from threading import Thread
import asyncio
from dotenv import load_dotenv
import pickle
import stock_order as stocks
from alpaca.trading.client import TradingClient
from alpaca.data.live.stock import StockDataStream
from alpaca.data.historical.stock import StockHistoricalDataClient
from alpaca.data.requests import StockLatestQuoteRequest
from alpaca.data.enums import DataFeed
from alpaca.data.models.bars import *
from alpaca.data.models.quotes import *

load_dotenv()
API_KEY = os.getenv("API-KEY")
print(API_KEY)
SECRET_KEY = os.getenv("SECRET-KEY")

model_f = open("./naivebayes.pickle", "rb")
model = pickle.load(model_f)
model_f.close()

print(model.__class__)

dataStream = StockDataStream(API_KEY, SECRET_KEY, feed=DataFeed.IEX)

recent_data = {}
owned_stocks = {}
    
def add_data(data: Quote):
    if(data.bid_price != 0):
        recent_data[data.symbol] = data.bid_price

def run():
    
    print("Bot Initializing...")
    
    #Initialize trading client, data client, and account
    client = TradingClient(API_KEY, SECRET_KEY, paper=True)
    dataClient = StockHistoricalDataClient(API_KEY, SECRET_KEY)
    account = client.get_account()
    
    positions = client.get_all_positions()

    for stock in positions:   
        dataStream.subscribe_quotes(data_handler, stock.symbol)
    
    loop_start_time = time.time()
    
    while(True):
        time_elapsed = loop_start_time - time.time()
        print(float(account.cash))
        if(float(account.cash) > 10000.0):
            print("buy")
            
            s = stocks.find_stock(client, dataClient)
            SYMBOL = s.get('symbol')            
            PRICE = s.get('price')
            NAME = s.get('name')
                
            dataStream.subscribe_quotes(data_handler, SYMBOL)
            print("Tracking data for {}".format(SYMBOL))
            
            SENTIMENT = stocks.determine_sentiment(s, model)


            stocks.place_order(client, s, SENTIMENT)
            
            owned_stocks[SYMBOL] = NAME
        elif(time_elapsed > 86400 or float(account.cash) < 10000):
            print("check")
            
            for info in stocks.find_positions_info(client, dataClient, owned_stocks):
                sentiment = stocks.determine_sentiment(info, model)
                
                stocks.place_order(client, info, sentiment, True)
            
        
        
async def data_handler(data: Quote):
    add_data(data)

async def main():
    dataStream_task = asyncio.create_task(dataStream._run_forever())
    
    botThread = Thread(target=run, name="bot")
    botThread.start()
    
    await dataStream_task
        
        
if __name__ == "__main__":
    asyncio.run(main())