import data
import server
from datetime import datetime, timezone
import pycoingecko
from generation import call_openai
import twitter

from pycoingecko import CoinGeckoAPI
cg = CoinGeckoAPI()

async def processCommand(command):
    full_case = command
    command = command.lower()
    if command.startswith("coingecko "):
        params = command.split(" ")
        if len(params) == 3:
            return str(cg.get_price(ids=params[1], vs_currencies=params[2]))
        else:
            return "Invalid number of parameters. The correct format is coingecko [cryptocurrency] [base currency]."
    elif command == "datetime":
        return "The current datetime (in day/month/year hour:minute format) is " + datetime.now(timezone.utc).strftime("%d/%m/%Y %H:%M")
    else:
        return "Unknown command."
