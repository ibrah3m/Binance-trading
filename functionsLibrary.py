import os
import dotenv
from dotenv import load_dotenv
from dotenv import dotenv_values
import binance.client
from binance.client import Client
from os.path import exists
import pandas as pd
import time
import datetime

load_dotenv()
Pkey = os.getenv("PubKey")
Skey = os.getenv("SecKey")
cTLD = os.getenv("TLD")

##Setting TLD
if cTLD:
    Client = Client(api_key=Pkey, api_secret=Skey, tld=cTLD)

else:
    Client = Client(api_key=Pkey, api_secret=Skey)

########################################################


def getDir(filename):
    basedir = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(basedir, filename)


# this will return the full dir with file name


def format_value(valuetoformatx, fractionfactorx):
    value = valuetoformatx
    fractionfactor = fractionfactorx
    Precision = abs(int(f"{fractionfactor:e}".split("e")[-1]))
    FormattedValue = float("{:0.0{}f}".format(value, Precision))
    return FormattedValue


# to format the input value to match the range for example 0.12345 to 0.124


def CheckIsThereOpenOrders(symbol, timestamp):
    trades = pd.DataFrame(Client.get_open_orders(symbol=symbol, timestamp=timestamp))
    if not trades.empty:
        return True
    else:
        return False


# check orders is there any open order in this $symbol


def recordorders(filename, data=""):
    if not exists(filename):
        file = pd.DataFrame(data).to_csv(filename, index=False)

    elif exists(filename):
        if os.path.getsize(filename) > 0:
            file = pd.read_csv(filename)
            olddata = pd.DataFrame(file)
            newdata = pd.DataFrame(data)
            data = olddata.append(newdata).to_csv(filename, index=False)
        elif os.path.getsize(filename) <= 0:
            file = pd.DataFrame(data).to_csv(filename, index=False)

    return file


# need to edit the location of saving
# have 3 cases
#     1- if the not exist
#     2- if file exist and not empty overwrite
#     3- if file is empty
#     and should return the file data


def PercentageCalc(numPercent, inputVal):
    percentage = (float(inputVal) / 100) * float(numPercent)
    return percentage


def OpenOrder(
    symbol, moneyCount=0, side="", TakeProfitPrice=0, StopPrice=0, SellExecQuantity=0
):
    price = Client.get_symbol_ticker(symbol=symbol)
    # right now price
    info = Client.get_symbol_info(symbol=symbol)

    Minquantity = pd.to_numeric(info["filters"][2]["minQty"])
    # the lowset quantity can be use for trade

    MinPrice = pd.to_numeric(info["filters"][0]["minPrice"])
    # the lowset price can be use for trade
    print(float(price["price"]))
    print(moneyCount)
    RightNowBuyQuantity = float(moneyCount) / float(price["price"])
    # quantity now to use it in buy order
    print(RightNowBuyQuantity)
    FormattedQuantitiy = format_value(RightNowBuyQuantity, Minquantity)
    # format the value and make it matche and used for market buy
    print(FormattedQuantitiy)

    FormattedSellQuantitiy = format_value(SellExecQuantity, MinPrice)
    # format the value and make it matche for sell

    TakeProfitPriceFormatted = format_value(TakeProfitPrice, MinPrice)
    # used in oco

    StopPriceFormatted = format_value(StopPrice, MinPrice)
    # used in oco
    StopLimitPriceFormatted = format_value(
        StopPriceFormatted - (StopPriceFormatted * MinPrice), MinPrice
    )
    # used in oco
    if side == "BUY":
        while True:
            time.sleep(1)
            try:
                MakebuyOrder = Client.order_market_buy(
                    symbol=symbol, quantity=FormattedQuantitiy
                )
                recordorders(getDir("buyorders.csv"), data=MakebuyOrder)
                return MakebuyOrder
                break
            except Exception as e:
                print(f"making limit order{e}")

    elif side == "SELL":

        while True:
            time.sleep(1)
            try:

                MakesellOrder = Client.order_oco_sell(
                    symbol=symbol,
                    quantity=FormattedSellQuantitiy,
                    price=TakeProfitPriceFormatted,
                    stopPrice=StopPriceFormatted,
                    stopLimitPrice=StopLimitPriceFormatted,
                    stopLimitTimeInForce="GTC",
                )
                # price is the take profit and target

                recordorders(getDir("sellorders.csv"), data=MakesellOrder)

                # return MakesellOrder
                break
            except Exception as e:
                print(f"making sell order{e}")


# moneyCount from the balance how much
# TpTargetPercent out of 100
# StpTargetPercent out of 100
# timestamp from the script
#
#
#
def trade(symbol, moneyCount, TpTargetPercent, StpTargetPercent, timestamp):
    global currentorders

    # this check if there is any open orders
    # =================================
    currentorders = True
    while currentorders == True:
        try:

            currentorders = CheckIsThereOpenOrders(symbol, timestamp)
            if currentorders == True:

                print("pending order")

                time.sleep(1)

        except Exception as e:
            print(f"process pending order{e}")
            time.sleep(1)

    #  =====================================

    # making buy order and loop until make the order
    #  =====================================

    Buyorder = OpenOrder(symbol=symbol, moneyCount=moneyCount, side="BUY")

    while Buyorder == None:

        time.sleep(2)

    #  =====================================

    # sell order chosing
    #  =====================================
    ExecQuantity = pd.to_numeric(Buyorder["executedQty"])

    LivePrice = float(Client.get_symbol_ticker(symbol=symbol)["price"])

    BuyPrice = float(Buyorder["fills"][0]["price"])
    # print(f"buy order compeleted with this price : {BuyPrice}") replace with bot
    HighestPrice = 0
    # this price is result from comparing the buyprice and now price
    if BuyPrice > LivePrice:

        HighestPrice = BuyPrice

    else:

        HighestPrice = LivePrice

    # print(f"sell order  with this price : {BuyPrice}")  replace
    # print(f"sell order  with this sellquantity : {ExecQuantity}") replace

    #  =====================================

    # making sell order
    #  =====================================

    # sellorder = OpenOrder(
    #     symbol=symbol,
    #     side="SELL",
    #     SellExecQuantity=ExecQuantity,
    #     TakeProfitPrice=HighestPrice
    #     + PercentageCalc(numPercent=TpTargetPercent, inputVal=BuyPrice),
    #     StopPrice=BuyPrice
    #     - PercentageCalc(numPercent=StpTargetPercent, inputVal=BuyPrice),
    # )
    sellorder = OpenOrder(
        symbol=symbol,
        side="SELL",
        SellExecQuantity=ExecQuantity,
        TakeProfitPrice=TpTargetPercent,
        StopPrice=StpTargetPercent,
    )

    # while sellorder == None:
    #     time.sleep(1)

    # print(f"sell order compeleted with this price : {BuyPrice}")

    #  =====================================

    # send note if sell completed
    #  =====================================
    # oco1 = sellorder["orders"][0]["orderId"]
    # oco2 = sellorder["orders"][1]["orderId"]

    # while True:
    #     order1 = Client.get_order(symbol=symbol, orderId=oco1)
    #     order2 = Client.get_order(symbol=symbol, orderId=oco2)

    #     if order1["status"] == "FILLED" or order2["status"] == "FILLED":
    #         # print sell compeleted
    #         print("sell compeleted")
    #     break
    #     time.sleep(1)
    return "completed"


# check trend
# check str
