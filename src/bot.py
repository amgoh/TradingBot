import os
from dotenv import load_dotenv
import stock_order as client
from alpaca.trading.client import TradingClient
from alpaca.data.historical import StockHistoricalDataClient
import pickle

load_dotenv()
API_KEY = os.getenv("API-KEY")
SECRET_KEY = os.getenv("SECRET-KEY")

model_f = open("naivebayes.pickle", "rb")
model = pickle.load(model_f)
model_f.close()

#Initialize trading client and account
client = TradingClient(API_KEY, SECRET_KEY, paper=True)
account = client.get_account()

#Initialize stock data client
dataClient = StockHistoricalDataClient(API_KEY, SECRET_KEY)

#Calculate current profit/loss value
balance_change = float(account.equity) - float(account.last_equity)