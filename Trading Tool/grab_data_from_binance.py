import pandas as pd
import math
import os.path
from binance.client import Client
from datetime import datetime
from dateutil import parser


binance_api_key = '[REDACTED]'
binance_api_secret = '[REDACTED]'

batch_size = 1000
binance_client = Client(api_key=binance_api_key, api_secret=binance_api_secret)


class OHLCV:
    # OHLCV
    def __init__(self, timestamp, open_price, high, low, close, volume):
        self.timestamp = timestamp
        self.open = open_price
        self.high = high
        self.low = low
        self.close = close
        self.volume = volume

def minutes_of_new_data(symbol, kline_size, data, date, source):
    if len(data) > 0:
        old = parser.parse(data["timestamp"].iloc[-1])
    elif source == "binance":
        old = datetime.strptime(date, '%Y-%m-%d')  # Convert Date to the good format
    if source == "binance":
        # try handle connect binance
        try:
            binance_connection = binance_client.get_klines(symbol=symbol, interval=kline_size)
        except Exception as e:
            print(f"Fehler bei der Verbindungsherstellung zu Binance, Error Msg:{e}")
        new = pd.to_datetime(binance_connection[-1][0], unit='ms')
    return old, new

def get_all_binance(symbol, kline_size, start_date, save=False):
    start_input = start_date
    print("Start date:", start_input)  # Startdatum "Format YYYY-MM-DD"
    filename = '%s-%s-data.csv' % (symbol, kline_size)


    if os.path.isfile(filename):
        data_df = pd.read_csv(filename)
    else:
        data_df = pd.DataFrame()

    oldest_point, newest_point = minutes_of_new_data(symbol, kline_size, data_df, start_input, source="binance")
    delta_min = (newest_point - oldest_point).total_seconds() / 60
    available_data = math.ceil(delta_min / binsizes[kline_size])

    if oldest_point == datetime.strptime('1 Jan 2017', '%d %b %Y'):
        print('Downloading all available %s data for %s. Be patient..!' % (kline_size, symbol))
    else:
        print('Downloading %d minutes of new data available for %s, i.e. %d instances of %s data.' % (
            delta_min, symbol, available_data, kline_size))

    klines = binance_client.get_historical_klines(
        symbol,
        kline_size,
        oldest_point.strftime("%d %b %Y %H:%M:%S"),  
        newest_point.strftime("%d %b %Y %H:%M:%S") 
    )

    ohlcv_data = [
        OHLCV(
            timestamp=pd.to_datetime(kline[0], unit='ms'),
            open_price=float(kline[1]),
            high=float(kline[2]),
            low=float(kline[3]),
            close=float(kline[4]),
            volume=float(kline[5])
        ) for kline in klines
    ]

   
    if save:
        pd.DataFrame([vars(ohlcv) for ohlcv in ohlcv_data]).to_csv(filename, index=False)

    print('All caught up..!')
    #print(ohlcv_data)
    return ohlcv_data

binsizes = {
    "1m": 1,
    "3m": 3,
    "5m": 5,
    "15m": 15,
    "30m": 30,
    "1h": 60,
    "2h": 120,
    "4h": 240,
    "6h": 360,
    "8h": 480,
    "12h": 720,
    "1d": 1440,
    "3d": 4320,
    "1w": 10080,
    "1M": 43200,
}
