import websocket
import json
import talib
import numpy
import pandas as pd
import telebot
import datetime
from binance.client import *
import logging

TICKER = 'btcusdt'
RSI_PERIOD = 14
MA_PERIOD = 9
ATR_PERIOD = 14
TREND_FLOAT = 1
RSI_DIFFERENCE_FLOAT = 0.3
TREND_SPECTATING_LENGTH = 20
TP_const = 1
SL_const = 0.3


logging.basicConfig(filename='logs.log', level=logging.INFO, format='%(asctime)s:%(message)s')
pd.set_option('display.max_rows', None)
pd.set_option('display.max_columns', None)
pd.options.mode.chained_assignment = None
bot = telebot.TeleBot('5296286497:AAGkHGl-R8_K3s8jCXvTq66VXLaj25KZKeU')
bot.config['api_key'] = '5296286497:AAGkHGl-R8_K3s8jCXvTq66VXLaj25KZKeU'

client = Client('BINANCE API',
                'Binance API Key')

url = 'wss://fstream.binance.com:443/ws/' + TICKER + '@kline_1m'

closes = []
ETHTREND = False





data = client.futures_klines(symbol=TICKER.upper(), interval=Client.KLINE_INTERVAL_1MINUTE, limit=1500)
cut_data = []
for i in data:
    i[0] = datetime.datetime.fromtimestamp(int(i[0]) / 1000).strftime('%B %#d, %Y %H:%M:%S')
    cut_data.append(i[0:6])
df = pd.DataFrame(cut_data[:-1], columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
print(df.tail())


def on_open(ws):
    print('Opened connection')
    try:
        q = 1
        # message = bot.send_message('459862465', 'The bot has opened the connection Pycharm')
    except Exception as err:
        print(err)


def on_close(ws):
    print('Connection closed')
    bot.send_message('459862465', 'The bot has closed the connection')

def check_result(df, index, entry, side = 'Sell'):
    tf = df.iloc[index+1:, ]


    for i in tf.index:
        if float(tf.at[i, 'high']) > float(entry) * (1 + TP_const / 100) and side == 'Buy':
            return True
            break
        elif float(tf.at[i, 'low']) < float(entry) * (1 - SL_const / 100) and side == 'Buy':
            return False
            break
        elif float(tf.at[i, 'low']) < float(entry) * (1-TP_const/100) and side == 'Sell':
            return True
            break
        elif float(tf.at[i, 'high']) > float(entry) * (1+SL_const/100) and side == 'Sell':
            return False
            break




def on_message(ws, message):
    global closes
    global ETHTREND
    global upindexes
    json_message = json.loads(message)
    # pprint.pprint(json_message)
    candle = json_message['k']
    is_candle_closed = candle['x']
    close = candle['c']

    if is_candle_closed:
        print('Candle closed at {}'.format(close))
        time_of_candle = datetime.datetime.fromtimestamp(int(candle['T']) / 1000).strftime('%B %#d, %Y %H:%M:%S')
        df.loc[df.shape[0]] = [time_of_candle, candle['o'], candle['h'], candle['l'], candle['c'], candle['v']]
        if df.count()['timestamp'] > RSI_PERIOD:
            np_close = numpy.array([float(i) for i in (df['close'].to_list())])
            np_high = numpy.array([float(i) for i in (df['high'].to_list())])
            np_low = numpy.array([float(i) for i in (df['low'].to_list())])

            rsi = talib.RSI(np_close, RSI_PERIOD)
            ma = talib.MA(np_close, MA_PERIOD)
            atr = talib.ATR(np_high, np_low, np_close, ATR_PERIOD)
            macd = talib.MACD(np_close, fastperiod=12, slowperiod=26, signalperiod=9)
            main_dataframe = df.assign(Rsi=rsi.tolist(), MA=ma.tolist(), ATR=atr.tolist(), MACD=macd[0].tolist(),
                                       MACD1=macd[1].tolist(), Signal=macd[2].tolist())
            df_sorted = main_dataframe



            try:
                df_sorted['Shift'] = df_sorted.Signal.shift(periods= 1)
                print(df_sorted.tail(160))

                buy_signal = df_sorted.tail(1450)[(df_sorted.Signal > 0) & (df_sorted.Shift < 0) & (df_sorted.MACD < 0) & (df_sorted.MACD1 < 0)]
                print(buy_signal)

                sell_signal = df_sorted.tail(1450)[(df_sorted.Signal < 0) & (df_sorted.Shift > 0) & (df_sorted.MACD > 0) & (df_sorted.MACD1 > 0)]
                print(sell_signal)

                def check(table, side):
                    RS = []
                    # print(table)
                    for row in table.index:

                        result = check_result(df_sorted, row, df_sorted.at[row, 'close'], side)

                        if result == True:
                            # print('Vigrash')
                            RS.append('V')
                        if result == False:
                            # print('Progrash')
                            RS.append('L')
                        if result == None:
                            RS.append('NE')

                    return RS


                buy_signal['result'] = check(buy_signal, 'Buy')
                print(buy_signal)

                sell_signal['result'] = check(sell_signal, 'Sell')
                print(sell_signal)


                excel = pd.concat([buy_signal, sell_signal])
                print(excel)

                with pd.ExcelWriter('out.xlsx') as writer:
                    excel.to_excel(writer, sheet_name='result')


            except Exception as err:
                print(err)









ws = websocket.WebSocketApp(url, on_open=on_open, on_close=on_close, on_message=on_message)
ws.run_forever()

'''

 
  
backup






import websocket
import json
import talib
import numpy
import pandas as pd
import telebot
import datetime
from binance.client import *

TICKER = 'ethusdt'
RSI_PERIOD = 14
MA_PERIOD = 9
ATR_PERIOD = 14
TREND_FLOAT = 1
RSI_DIFFERENCE_FLOAT = 0.3
TREND_SPECTATING_LENGTH = 20

pd.set_option('display.max_rows', None)
pd.set_option('display.max_columns', None)
pd.options.mode.chained_assignment = None
bot = telebot.TeleBot('5256286497:AAGkHGl-R8_K3s8jCXvTq66VXLaj2cKZKeU')
bot.config['api_key'] = '5256286497:AAGkHGl-R8_K3s8jCXvTq66VXLaj2cKZKeU'

client = Client('LdG8pzxTyxFK0YAffKVxYcM8asVs7plpx7LWAbjR23ERJDLHDD4HTGIsdVPQJd3r',
                'fKHygtJYShM4dlIi18zyD4FmoezDFAnMfjBuriVPUnJDOBu5saKubddaSf5c44g2')

url = 'wss://fstream.binance.com:443/ws/' + TICKER + '@kline_1m'

closes = []
ETHTREND = False

data = client.futures_klines(symbol=TICKER.upper(), interval=Client.KLINE_INTERVAL_1MINUTE, limit=200)
cut_data = []
for i in data:
    i[0] = datetime.datetime.fromtimestamp(int(i[0]) / 1000).strftime('%B %#d, %Y %H:%M:%S')
    cut_data.append(i[0:6])
df = pd.DataFrame(cut_data[:-1], columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
print(df.tail())


def on_open(ws):
    print('Opened connection')
    try:
        q = 1
        # message = bot.send_message('459862465', 'The bot has opened the connection Pycharm')
    except Exception as err:
        print(err)


def on_close(ws):
    print('Connection closed')
    bot.send_message('459862465', 'The bot has closed the connection')


def on_message(ws, message):
    global closes
    global ETHTREND
    global upindexes
    json_message = json.loads(message)
    # pprint.pprint(json_message)
    candle = json_message['k']
    is_candle_closed = candle['x']
    close = candle['c']

    if is_candle_closed:
        print('Candle closed at {}'.format(close))
        time_of_candle = datetime.datetime.fromtimestamp(int(candle['T']) / 1000).strftime('%B %#d, %Y %H:%M:%S')
        df.loc[df.shape[0]] = [time_of_candle, candle['o'], candle['h'], candle['l'], candle['c'], candle['v']]
        if df.count()['timestamp'] > RSI_PERIOD:
            np_close = numpy.array([float(i) for i in (df['close'].to_list())])
            np_high = numpy.array([float(i) for i in (df['high'].to_list())])
            np_low = numpy.array([float(i) for i in (df['low'].to_list())])

            rsi = talib.RSI(np_close, RSI_PERIOD)
            ma = talib.MA(np_close, MA_PERIOD)
            atr = talib.ATR(np_high, np_low, np_close, ATR_PERIOD)
            macd = talib.MACD(np_close, fastperiod=12, slowperiod=26, signalperiod=9)
            main_dataframe = df.assign(Rsi=rsi.tolist(), MA=ma.tolist(), ATR=atr.tolist(), MACD=macd[0].tolist(),
                                       MACD1=macd[1].tolist(), Signal=macd[2].tolist())
            df_sorted = main_dataframe



            try:
                df_sorted['Shift'] = df_sorted.Signal.shift(periods= 1)
                print(df_sorted.tail(160))

                buy_signal = df_sorted.tail(160)[(df_sorted.Signal > 0) & (df_sorted.Shift < 0) & (df_sorted.MACD < 0) & (df_sorted.MACD1 < 0)]
                print(buy_signal)

                sell_signal = df_sorted.tail(160)[(df_sorted.Signal < 0) & (df_sorted.Shift > 0) & (df_sorted.MACD > 0) & (df_sorted.MACD1 > 0)]
                print(sell_signal)




            except Exception as err:
                print(err)









ws = websocket.WebSocketApp(url, on_open=on_open, on_close=on_close, on_message=on_message)
ws.run_forever()

----------------------------------------------------------------------------------------------------------------------------------------------



            for index, row in df_sorted.iterrows():
                try:
                    if float(row['low']) < float(row['MA'] - TREND_FLOAT * float(row['ATR'])):
                        print('True low : ' + str(index) + 'Timestamp: '+str(row['timestamp']))
                        low_debug.append(float(row['low']))
                except Exception as err:
                    print(err)



            previous_low = min(low_debug)
            print(previous_low)

            print(type(df_sorted.low[80]))
            print(type(previous_low))
            previous_low_index = df_sorted.low[df_sorted.low == str(previous_low)].index.tolist()[0]
            print(previous_low_index)
            previous_low_MA = main_dataframe['MA'][previous_low_index]
            print(previous_low_MA)
            previous_low_ATR = main_dataframe['ATR'][previous_low_index]
            print(previous_low_ATR)
            previous_low_RSI = main_dataframe['Rsi'][previous_low_index]
            print(previous_low_RSI)
            current_low = main_dataframe['low'].tolist()[-1]
            print(current_low)
            current_RSI = main_dataframe['Rsi'].tolist()[-1]
            print(current_RSI)



            print(TREND_FLOAT)
            print(RSI_DIFFERENCE_FLOAT)

            try:
                bool1 = float(previous_low) < float(previous_low_MA - TREND_FLOAT * previous_low_ATR)
                bool2 = float(current_low) < float(previous_low)
                bool3 = float(current_RSI) - float(previous_low_RSI) > float(RSI_DIFFERENCE_FLOAT)
                print(bool1)
                print(bool2)
                print(bool3)
                print(main_dataframe)
                if previous_low < previous_low_MA - TREND_FLOAT * previous_low_ATR and current_low < previous_low and current_RSI - previous_low_RSI > RSI_DIFFERENCE_FLOAT:
                    bot.send_message('459862465', 'We have got a buy signal!!! Timestamp is: ' + main_dataframe['timestamp'].tolist()[-1] + ' and price is ' + main_dataframe['close'].tolist()[-1])
                    print('BUY BUY BUY')
            except Exception as err:
                print(err)



'''

