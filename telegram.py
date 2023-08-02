# To add a new cell, type '# %%'
# To add a new markdown cell, type '# %% [markdown]'
# %%
import telepot
import pandas as pd
bot = telepot.Bot('1913570782:AAHIrTJDK7-toxsxqOv27Dh9wYU2d5HYfgk')
bot.getMe()
import requests
import time
import urllib
from datetime import date

import pandas as pd
import time
import sys

# local modules
from binance.client import Client
from binance.enums import *
from indicator import indicators

# local file
import secrets
from configparser import ConfigParser
import yfinance as yf
import numpy as np
import datetime as dt
import requests 
import json 
import pandas as pd 
import numpy as np  
from finta import TA

df3 = pd.read_csv("parameters.csv")
df3.set_index("parameters",inplace=True)
df1=df3.T
client = Client((df1['binance_api_key'][0]), str(df1['binance_api_secret_key'][0]))
j=0


# %%

while True:
    try:
        from pprint import pprint
        response = bot.getUpdates()
        pprint(response)    

        if len(response)>j:
            if 'document' in response[-1]['message']:
                
                # if response[-1]['message']['document']['file_name'].upper()=='STOCKS.CSV':
                    
                #     file_id=response[-1]['message']['document']['file_id']
                
                #     endpoint=r"https://api.telegram.org/bot1715056219:AAGxytb3U1gIt1vlVn8Jf5b4za3E1HPuOd4/getFile?file_id={}".format(file_id)
                #     content=requests.get(url=endpoint)
                #     content=content.json()
                
                #     file_path=content['result']['file_path']
                #     endpoint=r"https://api.telegram.org/file/bot1715056219:AAGxytb3U1gIt1vlVn8Jf5b4za3E1HPuOd4/{}".format(file_path)
                #     req = requests.get(endpoint)
                #     url_content = req.content
                #     csv_file = open('stocks.csv', 'wb')
                
                #     csv_file.write(url_content)
                #     csv_file.close()
                
                #     bot.sendDocument(1039725953, document=open('stocks.csv', 'rb'))
                #     bot.sendMessage(1039725953,'please veriy if the stocks are updated or not')

                if 'PARAMETERS' in response[-1]['message']['document']['file_name'].upper():
                    file_id=response[-1]['message']['document']['file_id']
                
                    endpoint=r"https://api.telegram.org/bot1913570782:AAHIrTJDK7-toxsxqOv27Dh9wYU2d5HYfgk/getFile?file_id={}".format(file_id)
                    content=requests.get(url=endpoint)
                    content=content.json()
                
                    file_path=content['result']['file_path']
                    endpoint=r"https://api.telegram.org/file/bot1913570782:AAHIrTJDK7-toxsxqOv27Dh9wYU2d5HYfgk/{}".format(file_path)
                    req = requests.get(endpoint)
                    url_content = req.content
                    csv_file = open('parameters.csv', 'wb')
                
                    csv_file.write(url_content)
                    csv_file.close()
                
                    bot.sendDocument(1039725953, document=open('parameters.csv', 'rb'))
                    bot.sendDocument(665596324, document=open('parameters.csv', 'rb'))
                    bot.sendMessage(1039725953,'please veriy if the parameters are updated or not')
                    bot.sendMessage(665596324,'please veriy if the parameters are updated or not')

                
            else:
                message=response[-1]['message']['text']
                
                message=message.upper()
                # if message=='SEE STOCKS':
                    
                #     bot.sendDocument(1039725953, document=open('stocks.csv', 'rb'))

                # if message=='CHANGE STOCKS':
                #     bot.sendMessage(1039725953,'please first write "SEE STOCKS" and have the list of presently running stocks and make all the changes you want and then send it back' )


                if message=='SEE PARAMETERS':
                    bot.sendDocument(1039725953, document=open('parameters.csv', 'rb'))
                    bot.sendDocument(665596324, document=open('parameters.csv', 'rb'))

                elif message=='STOP BOT':
                    df3 = pd.read_csv("parameters.csv")
                    df3['value'].iloc[-1]= 'off'
                    df3.to_csv('parameters.csv')
                    bot.sendMessage(1039725953,'Bot has been stopped')
                    bot.sendMessage(665596324,'Bot has been stopped')


                elif message=='START BOT':

                    df3 = pd.read_csv("parameters.csv")
                    df3['value'].iloc[-1]= 'on'
                    df3.to_csv('parameters.csv')
                    bot.sendMessage(1039725953,'Bot has been started')
                    bot.sendMessage(665596324,'Bot has been started')






        j=len(response)
    except Exception as e:
        bot.sendMessage(1039725953,str(e))

# %%



# %%
