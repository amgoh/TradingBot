from alpaca.trading.requests import GetAssetsRequest
from alpaca.trading.enums import AssetClass
from alpaca.trading.requests import MarketOrderRequest
from alpaca.trading.enums import OrderSide, TimeInForce
from alpaca.data.requests import StockLatestBarRequest
import webscraper as web
import random

def find_stock(tradeClient, dataClient) -> dict[str]:
    """
    Used to select a random tradable stock from a list of all U.S. Equities
    
    Returns: 
        A dict containing the name, symbol, price, and perceived sentiment related to the stock
    """
    #Get a list of all stocks
    search_params = GetAssetsRequest(asset_class=AssetClass.US_EQUITY)
    assets = tradeClient.get_all_assets(search_params)
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
    
    # Return value, dict
    stock_info = {
        'name' : STOCK,
        'symbol' : SYMBOL,
        'price' : PRICE
    }
    
    return stock_info

def find_stock_list(tradeClient, n) -> list[dict[str]]:
    """
    Used to select 'n' random tradable stocks from a list of all U.S. Equities
    
    Returns: 
        A list of 'n' dicts containing the name, symbol, price, and perceived sentiment related to the stock
    """
    
    stock_list = []
    
    for i in range(n):
        stock_list.append(find_stock(tradeClient))
    
    return stock_list

def determine_sentiment(stock_info, nltk_classifier):
    """
    Evaluate the current opinion of the stock based on a NaiveBayesClassifier 
    and the 10 most popular news articles on Google in the last 24 hours about the stock company
    
    Parameter:
        stock_info - A dict containing the stock info, can find info for random stock using find_stock() function
    """
    STOCK = stock_info.get('name')
    
    SENTIMENT = web.predict_stock_opinion(STOCK, nltk_classifier)
    
    return SENTIMENT

def place_order(client, stock_info, sentiment):
    """
    Places a buy/sell order based on the given stock info
    
    Parameter:
        stock_info - A dict containing the stock info, can find info for random stock using find_stock() function
    """
    
    stock_name = stock_info.get('name')
    stock_symbol = stock_info.get('symbol')
    stock_price = stock_info.get('price')
    
    match sentiment:
        case "neg":
            try:
                num_shares = client.get_open_position(stock_symbol).qty
                
                market_order_data = MarketOrderRequest(
                            symbol=stock_symbol,
                            qty=num_shares,
                            side=OrderSide.SELL,
                            time_in_force=TimeInForce.DAY
                )
                
                client.submit_order(
                    order_data=market_order_data
                )
                
                print("Sold {} shares of {} ({}) at ${}.".format(num_shares, stock_symbol, stock_name, stock_price))
            except:
                place_order(find_stock())
        case "pos":
            market_order_data = MarketOrderRequest(
                        symbol=stock_symbol,
                        qty=1000/stock_price,
                        side=OrderSide.BUY,
                        time_in_force=TimeInForce.DAY
            )
            
            client.submit_order(
                order_data=market_order_data
            )
            
            print("Bought {} shares of {} ({}) at ${}.".format(1000/stock_price, stock_symbol, stock_name, stock_price))
