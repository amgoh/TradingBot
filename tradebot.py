import os
from dotenv import load_dotenv
from alpaca.trading.client import TradingClient
from alpaca.trading.requests import GetAssetsRequest
from alpaca.trading.enums import AssetClass
from alpaca.trading.requests import MarketOrderRequest
from alpaca.trading.enums import OrderSide, TimeInForce
import webscraper as web


load_dotenv()
API_KEY = os.getenv("API-KEY")
SECRET_KEY = os.getenv("SECRET-KEY")


#Initialize trading client and account
client = TradingClient(API_KEY, SECRET_KEY, paper=True)
account = client.get_account()

#Check if account is available to trade
if(account.trading_blocked):
    print('Account is currently restricted from trading.')

#Calculate current profit/loss value
balance_change = float(account.equity) - float(account.last_equity)

search_params = GetAssetsRequest(asset_class=AssetClass.US_EQUITY)

assets = client.get_all_assets(search_params)

# for i in assets:
#     if i.symbol.startswith("Z") and i.tradable:
#         print(i.symbol)
        
# preparing market order
market_order_data = MarketOrderRequest(
                    symbol="SPY",
                    qty=0.023,
                    side=OrderSide.BUY,
                    time_in_force=TimeInForce.DAY
                    )

# Market order
market_order = client.submit_order(
                order_data=market_order_data
               )

print('${} is available as buying power.'.format(account.buying_power))
print(f'Today\'s portfolio balance change: ${balance_change}')