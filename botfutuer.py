import os
import time
import datetime

###################### BinanceAPI ######################
import functionsLibraryfutures
import stra

#################### Discord Logger ####################
# from discord_logger import DiscordLogger
from discord_logger import DiscordLogger
from datetime import datetime, timedelta, timezone

######################## dotenv ########################
import dotenv
from dotenv import load_dotenv
from dotenv import dotenv_values

load_dotenv()
##################### Variables ########################
Symbol = os.getenv("Symbol")
moneyCount = os.getenv("tradingBalance")
TpTargetPercents = os.getenv("TpTargetPercent")
StpTargetPercents = os.getenv("StpTargetPercent")
(
    checkbelow,
    checkabove,
    lastClosePrice,
    StpTargetPercent,
    TpTargetPercent,
) = stra.trend5MG()
timestamp = int(datetime.today().timestamp() * 1000)


def OrderLogger():
    logger = DiscordLogger(
        webhook_url="https://discord.com/api/webhooks/851193561839173652/OdB2ZcEUxvxLXyZE-Gvmt0tKbqD91aFD4RteSxtUlcjDlwRR2WHKN_ZaU6_60MOrUzLM",
        **LoggerOptions,
    )
    logger.construct(
        title="Buy Order",
        description=f" trend up , time {datetime.utcnow()}  ",
    )
    response = logger.send()


optionsstarted = {
    "application_name": "Binance Bot",
    "service_name": "Status",
    "service_icon_url": "https://cryptologos.cc/logos/binance-coin-bnb-logo.png",
    "display_hostname": False,
    "default_level": "default",
}

#################### Logger Options ####################
LoggerOptions = {
    "application_name": "Binance Bot",
    "service_name": "Bot Logger",
    "service_icon_url": "https://cryptologos.cc/logos/binance-coin-bnb-logo.png",
    "display_hostname": False,
    "default_level": "info",
}

#################### Start Logger ####################

logger = DiscordLogger(
    webhook_url="https://discord.com/api/webhooks/851193561839173652/OdB2ZcEUxvxLXyZE-Gvmt0tKbqD91aFD4RteSxtUlcjDlwRR2WHKN_ZaU6_60MOrUzLM",
    **optionsstarted,
)
logger.construct(title="Status Check", description="Bot Started!")
response = logger.send()

for x in range(500):
    while True:

        (
            checkbelow,
            checkabove,
            lastClosePrice,
            StpTargetPercent,
            TpTargetPercent,
        ) = stra.trend5MG()
        trenddirection, new, sort = stra.MoveAverage()

        if (
            checkabove == True
            and checkbelow == False
            and trenddirection == True
            and new == True
            and sort == True
        ):
            OrderLogger()
            trade = functionsLibraryfutures.trade(
                symbol=Symbol,
                moneyCount=moneyCount,
                TpTargetPercent=TpTargetPercents,
                StpTargetPercent=StpTargetPercents,
                timestamp=timestamp,
            )

            print(trade)
            if trade == True:
                time.sleep(300)

        else:
            time.sleep(1)
            print("trend waiting")

        time.sleep(1)

