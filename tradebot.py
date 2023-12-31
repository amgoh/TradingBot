import os
from dotenv import load_dotenv
from alpaca.trading.client import TradingClient
from alpaca.trading.requests import GetAssetsRequest
from alpaca.trading.enums import AssetClass
from alpaca.trading.requests import MarketOrderRequest
from alpaca.trading.enums import OrderSide, TimeInForce
from alpaca.data.requests import StockLatestBarRequest
from alpaca.data.historical import StockHistoricalDataClient
import webscraper as web
import random
import pickle

load_dotenv()
API_KEY = os.getenv("API-KEY")
SECRET_KEY = os.getenv("SECRET-KEY")

classifier_file = open("naivebayes.pickle", "rb")
classifier = pickle.load(classifier_file)
classifier_file.close()


#Initialize trading client and account
client = TradingClient(API_KEY, SECRET_KEY, paper=True)
account = client.get_account()

#Initialize stock data client
dataClient = StockHistoricalDataClient(API_KEY, SECRET_KEY)

#Calculate current profit/loss value
balance_change = float(account.equity) - float(account.last_equity)

#Get a list of all stocks
search_params = GetAssetsRequest(asset_class=AssetClass.US_EQUITY)
assets = client.get_all_assets(search_params)


def find_stock():
    """
    Used to select a random tradable stock from a list of all U.S. Equities
    
    Returns: 
        A dict containing the name, symbol, price, and perceived sentiment related to the stock
    """
    asset = random.choice(assets) # choose random stock from assets list

    # make sure selected asset is tradable on Alpaca
    while(not asset.tradable):
        asset = random.choice(assets)

    STOCK = asset.name # stock name
    SYMBOL = asset.symbol # stock symbol
    
    # Search for the latest stock pricing information for the random stock
    REQUEST_PARAMS = StockLatestBarRequest(symbol_or_symbols=SYMBOL)
    STOCK_BARS = dataClient.get_stock_latest_bar(REQUEST_PARAMS)
    PRICE = STOCK_BARS.get(SYMBOL).vwap # stock price
    
    # Evaluate the current opinion of the stock based on a NaiveBayesClassifier 
    # and the 10 most popular news articles in the last 24 hours about the stock company
    SENTIMENT = web.predict_stock_opinion(STOCK, classifier)
    
    # Return value, dict
    stock_info = {
        'name' : STOCK,
        'symbol' : SYMBOL,
        'price' : PRICE,
        'sentiment' : SENTIMENT
    }
    
    return stock_info

random_stock_info = find_stock()
stock_name = random_stock_info.get('name')
stock_symbol = random_stock_info.get('symbol')
stock_price = random_stock_info.get('price')
sentiment = random_stock_info.get('sentiment')

print('${} is available as buying power before purchasing {} stock.'.format(account.buying_power, stock_name))

match sentiment:
    case "neg":
        try:
            market_order_data = MarketOrderRequest(
                        symbol=stock_symbol,
                        qty=client.get_open_position(stock_symbol).qty,
                        side=OrderSide.SELL,
                        time_in_force=TimeInForce.DAY
            )
            
            market_order = client.submit_order(
                    order_data=market_order_data
            )
        except:
            print("not owned -> find new stock")
    case "pos":
        market_order_data = MarketOrderRequest(
                    symbol=stock_symbol,
                    qty=1000/stock_price,
                    side=OrderSide.BUY,
                    time_in_force=TimeInForce.DAY
        )
        
        market_order = client.submit_order(
                order_data=market_order_data
        )
        
print('$1000 has been spent on {} shares of {} stock, current buying power is : {}'.format(1000/stock_price, stock_name, account.buying_power))
print(f'Today\'s portfolio balance change: ${balance_change}')