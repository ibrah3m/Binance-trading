from operator import index
import os
from time import sleep
from dotenv import load_dotenv
from dotenv import dotenv_values
import binance.client
from binance.client import Client
from os.path import exists
from numpy import average
import pandas as pd
import time
from datetime import datetime, timedelta, timezone
import matplotlib.pyplot as plt

# start_time = time.time()

load_dotenv()
Pkey = os.getenv("PubKey")
Skey = os.getenv("SecKey")
cTLD = os.getenv("TLD")
Symbol = os.getenv("Symbol")


Client = Client(api_key=Pkey, api_secret=Skey)


def trend5MG():
    chart = Client.get_klines(symbol=Symbol, interval="1m", limit="5")
    chartTable = pd.DataFrame(chart)
    chartTable = chartTable.head(3)
    chartTable.columns = [
        "timestamp",
        "open",
        "high",
        "low",
        "close",
        "volume",
        "IGNORE",
        "quoteVolume",
        "SELLVolume",
        "BUY_VOL",
        "BUY_VOL_VAL",
        "x",
    ]
    del chartTable["IGNORE"]
    del chartTable["BUY_VOL"]
    del chartTable["quoteVolume"]
    del chartTable["BUY_VOL_VAL"]
    del chartTable["x"]
    del chartTable["SELLVolume"]
    chartTable["timestamp"] = pd.to_datetime(chartTable["timestamp"], unit="ms")
    # convert to numbers
    chartTable["open"] = pd.to_numeric(chartTable["open"])
    chartTable["high"] = pd.to_numeric(chartTable["high"])
    chartTable["low"] = pd.to_numeric(chartTable["low"])
    chartTable["close"] = pd.to_numeric(chartTable["close"])
    chartTable["volume"] = pd.to_numeric(chartTable["volume"])
    chartTable["trend"] = chartTable["close"] - chartTable["open"]
    chartTable["st"] = pd.to_numeric(chartTable["open"] - chartTable["low"])
    stcal = chartTable["st"].head(3).idxmax()
    # biggest one
    strow = chartTable.iloc[stcal]

    stl = strow.st + (strow.st / 100 * 10)
    tp = strow.st * 2

    stlPrice = strow["open"] - stl
    stlPercnet = (stl / strow["open"]) * 100
    tpPrice = strow["open"] + tp
    tpPercent = (tp / strow["open"]) * 100
    # print(tp)
    # print(stl)
    # print(chartTable.trend)
    # print(tpPercent)
    # print(stlPercnet)
    # ***** add different from 1 to 4 should be up to 1.5 like 85
    checkbelow = False
    checkabove = False
    for candil in chartTable.trend:
        if candil <= 0:
            checkbelow = True
        elif candil >= 0:
            checkabove = True
    # this pashe check if there's a red candil by seeing the different
    lastClosePrice = chartTable.loc[2]["close"]  # count start from 0

    return checkbelow, checkabove, lastClosePrice, stlPrice, tpPercent


def MoveAverage():
    chart = Client.get_klines(symbol=Symbol, interval="1m", limit="200")
    chartTable = pd.DataFrame(chart)

    chartTable.columns = [
        "timestamp",
        "open",
        "high",
        "low",
        "close",
        "volume",
        "IGNORE",
        "quoteVolume",
        "SELLVolume",
        "BUY_VOL",
        "BUY_VOL_VAL",
        "x",
    ]
    del chartTable["IGNORE"]
    del chartTable["BUY_VOL"]
    del chartTable["quoteVolume"]
    del chartTable["BUY_VOL_VAL"]
    del chartTable["x"]
    del chartTable["SELLVolume"]

    trend = chartTable.copy()
    trend["timestamp"] = pd.to_datetime(trend["timestamp"], unit="ms")
    trend["close"] = pd.to_numeric(chartTable.close)
    trend["5C"] = chartTable.close.rolling(5).mean()
    trend["10C"] = chartTable.close.rolling(10).mean()
    trend["21C"] = chartTable.close.rolling(21).mean()
    trend["Cx"] = trend["5C"] > trend["10C"]
    trend["sort"] = (trend["5C"].subtract(trend["10C"]) > 0) & (
        trend["10C"].subtract(trend["21C"]) > 0
    )

    # not work
    trend["po"] = trend["Cx"].diff().cumsum()
    trend = trend.dropna()
    trendx = trend.drop_duplicates(subset=["po"])
    # trend["close"].plot()
    # trend["10C"].plot(color="g")
    # trend["21C"].plot(color="r")
    # plt.plot(
    #     trendx["10C"][trendx["Cx"] == True].index,
    #     trendx["10C"][trendx["Cx"] == True],
    #     "^",
    #     markersize=25,
    #     color="g",
    #     label="buy",
    # )
    # plt.plot(
    #     trendx["10C"][trendx["Cx"] == False].index,
    #     trendx["10C"][trendx["Cx"] == False],
    #     "v",
    #     markersize=25,
    #     color="r",
    #     label="buy",
    # )
    # plt.show()

    last = trendx.iloc[-1:]
    # last row in the list(last X)
    Min40m = timedelta(minutes=30)
    # print(last["timestamp"] - Min40m)
    new = (datetime.utcnow() - last["timestamp"] < Min40m).bool()

    trenddirection = trendx.iloc[-1:]["Cx"].bool()
    sort = trend.iloc[-1:]["sort"].bool()
    # print(sort.to_string())
    # print(trend["5C"].subtract(trend["10C"]))
    # print(trend["10C"].subtract(trend["21C"]))

    #  0 down , 1 up
    return trenddirection, new, sort

    # select the last po
    # time
    # Min45m = datetime.time(minutes=5)


print(trend5MG())
print(MoveAverage())
# trenddirection, new, sort = MoveAverage()
# checkbelow, checkabove, lastClosePrice, stlPrice, tpPrice = trend5MG()
