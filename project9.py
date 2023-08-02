
# libraries 
import time

# local modules
import datetime as dt
# for seding request to binance and getting data
from binance.client import Client
from binance.enums import *


# data manipulation
import pandas as pd

# for POST and GET request
import requests

# json 
import json
# {
#     "dict":123,
#     "hello":23
# }

# for technical indicators
from finta import TA

# for telegram messages
import telepot


# connecting telegram bot
# telegram bot is made by botfather on telegram
# search botfather on telegram
# type /newbot
# finally we get information like 1913570782:AAHIrTJDK7-toxsxqOv27Dh9wYU2d5HYfgk
bot = telepot.Bot('1913570782:AAHIrTJDK7-toxsxqOv27Dh9wYU2d5HYfgk')
bot.getMe()



#reading 'parameters.csv'
# df3 -> dataframe (datatype)
df3 = pd.read_csv("parameters.csv")
df3.set_index("parameters",inplace=True)
# .T is used for transposing a dataframe
df1=df3.T




#logging in binance
client = Client((df1['binance_api_key'][0]), str(df1['binance_api_secret_key'][0]))




#historical data
def candle(symbol, interval):

    # root_url -> url where we are retrieving data from
    root_url = 'https://api.binance.com/api/v1/klines'
    url = root_url + '?symbol=' + symbol + '&interval=' + interval
    data = json.loads(requests.get(url).text)

    # data retrieve and converted to dataframe and saved in df variable
    df = pd.DataFrame(data)
    df.columns = ['Datetime',
                'Open', 'High', 'Low', 'Close', 'volume',
                'close_time', 'qav', 'num_trades',
                'taker_base_vol', 'taker_quote_vol', 'ignore']
    
    # datetime (timestamp -> datetime)
    df.index = [dt.datetime.fromtimestamp(x / 1000.0) for x in df.close_time]
    
    # droping the columns not needed
    df.drop(['close_time','qav','num_trades','taker_base_vol', 'taker_quote_vol', 'ignore'],axis=1,inplace=True)
           
    # strings to -> float value
    df['Open']=pd.to_numeric(df["Open"], downcast="float")
    df["High"]=pd.to_numeric(df["High"], downcast="float")
    df["Low"]=pd.to_numeric(df["Low"], downcast="float")
    df["Close"]=pd.to_numeric(df["Close"], downcast="float")
    df["volume"]=pd.to_numeric(df["volume"], downcast="float")


    # ATR indicator

    # made a new column named 'FIXED_ATR'
    df['FIXED_ATR']=TA.ATR(df,int(df1['atr_fixed'][0]))
    # Special data for special requirements of strategy.
    # calculating maximum and minimum values of last X BARS
    df['X_BARS_HIGH']=df['High'][-int(df1['X_bars_high'][0]):-1].max()
    df['X_BARS_LOW']=df['Low'][-int(df1['X_bars_low'][0]):-1].min()
    
    #atr value calulationg for 'TRAILING_ATR'
    df['TRAILING_ATR']=TA.ATR(df,int(df1['atr_trailing'][0]))
    
    # Datetime Open High Low Close Volume FIXED_ATR X_BARS_HIGH X_BARS_LOW TRAILING_ATR
    return df



#getting latest price of instrument
def ltp_price(instrument):
    prices = client.get_all_tickers()
    for i in range(len(prices)):
        if prices[i]['symbol']==str(instrument):
            return float(prices[i]['price'])

    



#order function for buy
def market_order():

    # NOOB Code -> should not put all the variables global, instead should put it in arguments
    global df,df1,distance_long,distance_short,buy_price,sell_price,quantity_buy,quantity_sell,fixed_buy_atr,fixed_sell_atr


    # present ATR VALUE In python -> -1 -> latest value
    fixed_buy_atr=float(df['FIXED_ATR'][-1])

    # balance of clients account
    p_l=float(client.futures_account_balance()[0]['balance'])

    # it is done so that we can be sure of what maximum loss we can take
    stoploss=float(df1['stop_loss_precentage'][0])/100 * p_l
    quantity_buy=int(stoploss/fixed_buy_atr)


    # uncomment for actually sending order on binance account

    # order = client.futures_create_order(
    #     symbol=str(df2['symbol_binance'][0]),
    #     side=Client.SIDE_BUY,
    #     type=Client.ORDER_TYPE_MARKET,
       
        
    #     quantity=float(df1['quantity'][0]))


    # noob method of doing
    buy_price=ltp_price(df1['symbol_binance'][0])

    l=1
    


#order function for sell
def market_order1():
    global df,df1,distance_long,distance_short,buy_price,sell_price,quantity_buy,quantity_sell,fixed_buy_atr,fixed_sell_atr
    
    fixed_sell_atr=float(df['FIXED_ATR'][-1])


    p_l=float(client.futures_account_balance()[0]['balance'])
    stoploss=float(df1['stop_loss_precentage'][0])/100 * p_l
    quantity_sell=int(stoploss/fixed_sell_atr)


    

    # order = client.futures_create_order(
    #     symbol=str(df1['symbol_binance'][0]),
    #     side=Client.SIDE_SELL,
    #     type=Client.ORDER_TYPE_MARKET,
    #     quantity=float(df1['quantity'][0]))

    sell_price=ltp_price(df1['symbol_binance'][0])

    l=1




#getting signal for buy/sell/squareoff's
def trade_signal(instrument,l_s):
    
    global df,df1,distance_long,distance_short,buy_price,sell_price,quantity_buy,quantity_sell,fixed_buy_atr,fixed_sell_atr,times1


    # current price of the currency
    ltp=ltp_price(df1['symbol_binance'][0])

    # initially signal is saved as ""
    signal=""

    if l_s=="":

        # if 5 minutes has already passed after starting the bot then times1 is updated
        if time.time()>times1+300:
            times1=time.time()


        # if current price -> is greater then X_BARS_HIGH current
        if ltp>float(df['X_BARS_HIGH'][-1]):
            signal="buy"
            


        # if current price -> is less then X_BARS_LOW current
        if ltp<float(df['X_BARS_LOW'][-1]):
            signal="sell"



    elif l_s=="long":

        # if distance between current value and current stoploss is 10% -> 10% = distance1_long
        distance1_long = ltp-df['TRAILING_ATR'][-1]*float(df1['atr_trailing_multiplier'][0])

        # trailing stoploss shifts 
        # shifts when price goes up
        if distance1_long>distance_long:
            distance_long=ltp-df['TRAILING_ATR'][-1]*float(df1['atr_trailing_multiplier'][0])


        # squares off if fixed stoploss is hit /or/ it gets below trailing stoploss (distance_long)
        if ltp<=buy_price-fixed_buy_atr*float(df1['atr_fixed_multiplier'][0]) or ltp<=distance_long:
            distance_long=0


            signal="squareoffsell"

        if time.time()>times1+300:
            times1=time.time()





    elif l_s=="short":

        
        distance1_short=ltp+df['TRAILING_ATR'][-1]*float(df1['atr_trailing_multiplier'][0])

        if distance1_short<distance_short:
            distance_short=ltp+df['TRAILING_ATR'][-1]*float(df1['atr_trailing_multiplier'][0])
        if ltp>=sell_price+fixed_sell_atr*float(df1['atr_fixed_multiplier'][0]) or ltp>=distance_short:
            distance_short=100000000000
            
            signal="squareoffbuy"


        if time.time()>times1+300:
            


            times1=time.time()


    return signal    


# %%


#main function
def main():
    global df,df1,distance_long,distance_short,buy_price,sell_price,quantity_buy,quantity_sell,fixed_buy_atr,fixed_sell_atr,position

    # reading parameters.csv file
    df3 = pd.read_csv("parameters.csv")
    df3.set_index("parameters",inplace=True)
    df1=df3.T


    # getting latest data about the symbol
    ltp=ltp_price(df1['symbol_binance'][0])
    


    #getting historical data
    df=candle(df1['symbol_binance'][0],str(df1['time_frame'][0]))

    
    # getting if there is a signal buy | sell | squuareoffbuy | squareoffsell
    signal=trade_signal(df1['symbol_binance'][0],position)

    


    #buying/selling/ squarring  off
    if signal=='buy':
        market_order()

        # variable which says that presently there is a 'long' position
        # this variable is used so that we dont have multiple buy /sell
        position='long'

        #sending update on telegram
        bot.sendMessage(1039725953,f"New long position initiated at {buy_price}")

  
  

    if signal=='sell':
        market_order1()
        position='short'
        bot.sendMessage(1039725953,f"New short position initiated at {sell_price}")

   
    
    if signal=="squareoffsell":
        market_order1()

        position=''
        bot.sendMessage(1039725953,f"long position squared of at {sell_price}")
        bot.sendMessage(1039725953,f" profit of {((sell_price-buy_price)/buy_price)*100*int(df1['binance_X'][0])}")

       
    if signal=="squareoffbuy":
        market_order()

        position=''
        bot.sendMessage(1039725953,f"short position squared of at {buy_price}")
        bot.sendMessage(1039725953,f" profit of {((sell_price-buy_price)/buy_price)*100*int(df1['binance_X'][0])}")



l=0
distance_short=100000000000
distance_long=0
times1=time.time()
position=''

#infinite loop
while True:
    try:
        # calling main function
        main()
        
    except Exception as e:
        bot.sendMessage(1039725953,str(e))


# CHATGPT -> tool || 