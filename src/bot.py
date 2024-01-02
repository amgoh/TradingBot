import os
import time
from threading import Thread
import asyncio
from dotenv import load_dotenv
import pickle
import stock_order as stocks
from alpaca.trading.client import TradingClient
from alpaca.data.live.stock import StockDataStream
from alpaca.data.enums import DataFeed
from alpaca.data.models.bars import *
from alpaca.data.models.quotes import *

load_dotenv()
API_KEY = os.getenv("API-KEY")
SECRET_KEY = os.getenv("SECRET-KEY")

model_f = open("naivebayes.pickle", "rb")
model = pickle.load(model_f)
model_f.close()

dataStream = StockDataStream(API_KEY, SECRET_KEY, feed=DataFeed.IEX)

recent_data = {}
    
def add_data(data: Quote):
    if(data.bid_price != 0):
        recent_data[data.symbol] = data.bid_price

def run():
    
    print("Bot Initializing...")
    
    #Initialize trading client and account
    client = TradingClient(API_KEY, SECRET_KEY, paper=True)
    account = client.get_account()
    
    positions = client.get_all_positions()
    
    for stock in positions:   
        dataStream.subscribe_quotes(data_handler, stock.symbol)
    
    loop_start_time = time.time()
    
    while(True):
        time_elapsed = loop_start_time - time.time()
        if(float(account.buying_power) - float(account.cash) > 10000):
            print("buy")
            
            s = stocks.find_stock(client)
            SYMBOL = s.get('symbol')
            NAME = s.get('name')
                
            dataStream.subscribe_quotes(data_handler, SYMBOL)
            
            while(not recent_data.get(SYMBOL)):
                None
            PRICE = recent_data.get(SYMBOL)
            
            SENTIMENT = stocks.determine_sentiment(s, model)
            
            stocks.place_order(client, s, PRICE, SENTIMENT)
        elif(time_elapsed > 120):
            print("check")
            
            for s in client.get_all_positions():
                SYMBOL = s.symbol
                
                while(not recent_data.get(s.symbol)):
                    None
                PRICE = recent_data.get(SYMBOL)
                
                info = {
                    'name' : SYMBOL,
                    'symbol' : SYMBOL,
                    'price' : PRICE
                }
                
                sentiment = stocks.determine_sentiment(info, model)
                
                info.pop('price')
                
                stocks.place_order(client, info, PRICE, sentiment, True)
            
        
        
async def data_handler(data: Quote):
    add_data(data)

async def main():
    dataStream_task = asyncio.create_task(dataStream._run_forever())
    
    botThread = Thread(target=run, name="bot")
    botThread.start()
    
    await dataStream_task
        
        
if __name__ == "__main__":
    asyncio.run(main())