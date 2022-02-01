import os
import time
import datetime

###################### BinanceAPI ######################
import functionsLibrary
import stra

#################### Discord Logger ####################
# from discord_logger import DiscordLogger
######################## dotenv ########################
import dotenv
from dotenv import load_dotenv
from dotenv import dotenv_values

load_dotenv()
##################### Variables ########################
Symbol = os.getenv("Symbol")
moneyCount = os.getenv("tradingBalance")
# TpTargetPercent = os.getenv("TpTargetPercent")
# StpTargetPercent = os.getenv("StpTargetPercent")
(
    checkbelow,
    checkabove,
    lastClosePrice,
    StpTargetPercent,
    TpTargetPercent,
) = stra.trend5MG()
timestamp = int(datetime.datetime.today().timestamp() * 1000)

for x in range(500):
    while True:

        (
            checkbelow,
            checkabove,
            lastClosePrice,
            StpTargetPercent,
            TpTargetPercent,
        ) = stra.trend5MG()
        if checkabove == True and checkbelow == False:
            if TpTargetPercent >= 0.3:
                break
            else:
                print("tp waiting")
                time.sleep(60)

        else:
            time.sleep(1)
            print("trend waiting")

    trade = functionsLibrary.trade(
        symbol=Symbol,
        moneyCount=moneyCount,
        TpTargetPercent=TpTargetPercent,
        StpTargetPercent=StpTargetPercent,
        timestamp=timestamp,
    )
    print(trade)
    time.sleep(400)

# Prices Fetch


# Buy

# Sell

# Logging

# Status
