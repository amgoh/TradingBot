from alpaca.trading.requests import GetAssetsRequest
from alpaca.trading.client import TradingClient
from alpaca.trading.enums import AssetClass
from alpaca.trading.requests import MarketOrderRequest
from alpaca.trading.enums import OrderSide, TimeInForce
from alpaca.data.historical.stock import StockHistoricalDataClient
from alpaca.data.requests import StockLatestQuoteRequest
from alpaca.data.models import Quote
import webscraper as web
import random

def find_stock(tradeClient: TradingClient, dataClient: StockHistoricalDataClient) -> dict[str]:
    """
    Used to select a random tradable stock from a list of all U.S. Equities
    
    Returns: 
        A dict containing the name, symbol, price, and perceived sentiment related to the stock
    """
    print("finding random stock...")
    #Get a list of all stocks
    search_params = GetAssetsRequest(asset_class=AssetClass.US_EQUITY)
    assets = tradeClient.get_all_assets(search_params)
    asset = random.choice(assets) # choose random stock from assets list

    # make sure selected asset is tradable on Alpaca
    while(not asset.tradable):
        asset = random.choice(assets)

    STOCK = asset.name # stock name
    SYMBOL = asset.symbol # stock symbol
    
    request_params = StockLatestQuoteRequest(symbol_or_symbols=SYMBOL)
    try:
        PRICE = dataClient.get_stock_latest_quote(request_params).get(SYMBOL).ask_price
        if(not PRICE):
            raise Exception("BID PRICE NOT FOUND")
    except Exception:
        return find_stock(tradeClient, dataClient)

    # Return value, dict
    stock_info = {
        'name' : STOCK,
        'symbol' : SYMBOL,
        'price' : PRICE
    }
    
    print("Found stock! -> {} ({}) is averaging at ${}".format(STOCK, SYMBOL, PRICE))
    
    return stock_info

def find_stock_list(tradeClient: TradingClient, dataClient: StockHistoricalDataClient, n: int) -> list[dict[str]]:
    """
    Used to select 'n' random tradable stocks from a list of all U.S. Equities
    
    Returns: 
        A list of 'n' dicts containing the name, symbol, price, and perceived sentiment related to the stock
    """
    
    stock_list = []
    
    for i in range(n):
        stock_list.append(find_stock(tradeClient, dataClient))
    
    return stock_list

def find_positions_info(tradeClient: TradingClient, dataClient: StockHistoricalDataClient, owned_stocks: dict[str, str]) -> list[dict[str]]:
    """
    Find the latest stock_info on all currently open positions

    Returns:
        A list of dicts containing the name, symbol, and price of all owned stock positions
    """

    positions = []

    for pos in owned_stocks:
        SYMBOL = pos
        NAME = owned_stocks.get(SYMBOL)
        
        request_params = StockLatestQuoteRequest(symbol_or_symbols=SYMBOL)
        data = dataClient.get_stock_latest_quote(request_params).get(SYMBOL)

        PRICE = data.bid_price
        
        info = {
            'name' : NAME,
            'symbol' : SYMBOL,
            'price' : PRICE
        }

        positions.append(info)
    
    return positions

def determine_sentiment(stock_info: dict[str], nltk_classifier):
    """
    Evaluate the current opinion of the stock based on a NaiveBayesClassifier 
    and the 10 most popular news articles on Google in the last 24 hours about the stock company
    
    Parameter:
        stock_info - A dict containing the stock info, can find info for random stock using find_stock() function
    """
    STOCK = stock_info.get('name')
    
    SENTIMENT = web.predict_stock_opinion(STOCK, nltk_classifier)
    
    print("{} is currently viewed as {}".format(STOCK, SENTIMENT))

    return SENTIMENT

def place_order(client: TradingClient, stock_info: dict[str], sentiment, owned = False):
    """
    Places a buy/sell order based on the given stock info
    
    Parameter:
        stock_info - A dict containing the stock name, stock symbol
    """
    
    STOCK = stock_info.get('name')
    SYMBOL = stock_info.get('symbol')
    PRICE = stock_info.get('price')
    
    match sentiment:
        case "neg":
            try:
                num_shares = client.get_open_position(SYMBOL).qty
                
                market_order_data = MarketOrderRequest(
                            symbol=SYMBOL,
                            qty=num_shares,
                            side=OrderSide.SELL,
                            time_in_force=TimeInForce.DAY
                )
                
                client.submit_order(
                    order_data=market_order_data
                )
                
                print("Sold {} shares of {} ({}) at ${}.".format(num_shares, SYMBOL,  STOCK, PRICE))
            except:
                print("Don't own {} stock, unable to place a SELL order".format(STOCK))
        case "pos":
            if(owned):
                sentiment = "none"
            try:
                print("trying to buy")
                market_order_data = MarketOrderRequest(
                            symbol=SYMBOL,
                            qty=10000/PRICE,
                            side=OrderSide.BUY,
                            time_in_force=TimeInForce.DAY
                )
                
                client.submit_order(
                    order_data=market_order_data
                )
                
                print("Bought {} shares of {} ({}) at ${}.".format(10000/PRICE, SYMBOL, STOCK, PRICE))
            except Exception:
                print("ERROR BUYING {}".format(SYMBOL))

    
    print("SUCCESSFUL ORDER OF {} STOCK".format(SYMBOL))
