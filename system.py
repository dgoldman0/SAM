import data
import server
from datetime import datetime, timezone
import pycoingecko
from generation import call_openai
import twitter
import weather

from pycoingecko import CoinGeckoAPI
cg = CoinGeckoAPI()

async def processCommand(command):
    full_case = command
    command = command.lower()
    if command.startswith("coingecko "):
        params = command.split(" ")
        if len(params) == 3:
            return "Coingecko data: " + str(cg.get_price(ids=params[1], vs_currencies=params[2]))
        else:
            return "Invalid number of parameters. The correct format is coingecko COINGECKO [comma separated list of cryptocurrencies] [comma separated list of base currencies]. Avoid spaces in a list."
    elif command == "datetime":
        return "The current datetime (in day/month/year hour:minute UTC format) is " + datetime.now(timezone.utc).strftime("%A %d/%m/%Y %H:%M")
    elif command.startswith("tweepy search "):
        json_args = full_case[14:]
        return "Tweepy recent search with parameters: " + json_args + "\nResults:\n" + twitter.search(json_args)
    elif command.startswith("weather "):
        params = command.split(" ")
        if len(params) == 3:
            return "Weather for location @ " + params[1] + 'lat, ' + params[2] + 'lon: ' + weather.currentWeather(float(params[1]), float(params[2]))
        else:
            return "Invalid number of parameters. The correct format is weather [lat] [lon]."
    else:
        return "Unknown command"
