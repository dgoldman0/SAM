import data
import server
from datetime import datetime, timezone
import pycoingecko
from generation import call_openai
import twitter
import weather
import news
import yelp

from pycoingecko import CoinGeckoAPI
cg = CoinGeckoAPI()

async def processCommand(command):
    full_case = command
    command = command.lower()
    if command.startswith("respond "):
        server.sendMessage(full_case[8:])
        return "Responded with:" + full_case[8:]
    elif command.startswith("coingecko "):
        params = command.split(" ")
        if len(params) == 3:
            if params[1].startswith('"') or params[2].startswith('"'):
                return "There is no need for quotation marks for the COINGECKO command."
            else:
                return "Coingecko data: " + str(cg.get_price(ids=params[1], vs_currencies=params[2]))
        else:
            return "Invalid number of parameters. The correct format is coingecko COINGECKO [comma separated list of cryptocurrencies] [comma separated list of base currencies]. Avoid spaces in a list."
    elif command.startswith("tweepy search "):
        json_args = full_case[14:]
        return "Tweepy recent search with parameters: " + json_args + "\nResults:\n" + twitter.search(json_args)
    elif command.startswith("tweepy tweet "):
        message = full_case[13:]
        return "Tweepy tweeted message: " + message + "\nResults:\n" + twitter.tweet(message)
    elif command.startswith("news "):
        json_args = full_case[5:]
        return "News search with search parameters: " + json_args + "\nResults:\n" + news.search(json_args)
    elif command.startswith("yelp "):
        params = command.split(" ")
        if len(params) == 4:
            return "Yelp results for search term " + params[1] + " @ " + params[2] + "lat, " + params[3] + "lon:" + yelp.search(params[1], str(params[2]), str(params[3]))
        else:
            return "Invalid number of parameters. The correct format is YELP [term] [lat] [lon]"
    elif command.startswith("weather "):
        params = command.split(" ")
        if len(params) == 3:
            return "Weather for location @ " + params[1] + 'lat, ' + params[2] + 'lon: ' + weather.currentWeather(float(params[1]), float(params[2]))
        else:
            return "Invalid number of parameters. The correct format is WEATHER [lat] [lon]."
    else:
        return "Unknown command: " + full_case + "\n" + "Please ensure that you did not miss any spaces and are using the correct format."

def now():
    return datetime.now(timezone.utc).strftime("%A %d/%m/%Y %H:%M")
