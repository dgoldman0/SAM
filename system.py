import data
import server
from datetime import datetime, timezone
import pycoingecko
from generation import call_openai
from generation import generate_image
import twitter
import weather
import news
import yelp
import requests
import html2text

from pycoingecko import CoinGeckoAPI
cg = CoinGeckoAPI()

async def processCommand(command):
    full_case = command
    command = command.lower()
    if command.startswith("respond "):
        server.sendMessage(full_case[8:])
        return "Responded with:" + full_case[8:]
    elif command.startswith("notation "):
        return "Temporary notation:" + full_case[9:]
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
    elif command.startswith("tweepy user "):
        return "Tweepy user info for " + command[12:] + ":\n" + twitter.userInfo(command[12:])
    elif command.startswith("tweepy followers #"):
        params = command[18:]
        list = params.split()
        id = list[0]
        next_token = None
        if len(params) == 2:
            next_token = list[1]

        return "Tweepy list of people following #" + id + " and next_token=" + str(next_token) + ":\n" + twitter.userFollowers(id, next_token)
    elif command.startswith("tweepy following #"):
        params = command[18:]
        list = params.split()
        id = list[0]
        next_token = None
        if len(params) == 2:
            next_token = list[1]

        return "Tweepy list of people following #" + id + " and next_token=" + str(next_token) + ":\n" + twitter.userFollowing(id, next_token)
    elif command.startswith("tweepy tweet "):
        message = full_case[13:]
        return "Tweepy tweeted message: " + message + "\nResults:\n" + twitter.tweet(message)
    elif command.startswith("news "):
        json_args = full_case[5:]
        return "News search with search parameters: " + json_args + "\nResults:\n" + news.search(json_args)
    elif command.startswith("yelp "):
        params = command.split(" ")
        if command.find('"') != -1:
            return "YELP command does not function with quotation marks. Exclude quotation marks."
        print(len(params))
        if len(params) == 4:
            return "Yelp results for search term " + params[1] + " @ " + params[2] + "lat, " + params[3] + "lon:" + yelp.search(params[1], str(params[2]), str(params[3]))
        else:
            return "Invalid number of parameters. The correct format is YELP [term] [lat] [lon]. As a reminder, only one command can be issued at a time."
    elif command.startswith("wcurrent "):
        params = command.split(" ")
        if len(params) == 3:
            return "Current weather (WCURRENT) for location @ " + params[1] + 'lat, ' + params[2] + 'lon: ' + weather.currentWeather(float(params[1]), float(params[2]))
        else:
            return "Invalid number of parameters. The correct format is WCURRENT [lat] [lon]."
    elif command.startswith("wday "):
        params = command.split(" ")
        if len(params) == 3:
            return "Seven day forecast (WDAY) starting with today, for location @ " + params[1] + 'lat, ' + params[2] + 'lon: ' + weather.sevenDay(float(params[1]), float(params[2]))
        else:
            return "Invalid number of parameters. The correct format is WDAY [lat] [lon]."
    elif command.startswith("image "):
        # Not working yet
        params = full_case.split(' ')
        prompt = ' '.join(params[2:])
        return "Image (size: " + params[1] + ") generated from prompt: " + prompt + "\nResult URL: " + generate_image(prompt, params[1])
    elif command.startswith("get "):
        url = full_case[4:]
        response = requests.get(url = url)
        text = html2text.html2text(response.text)
        try:
            return "Obtained data for URL " + url + "\n" + str(text)
        except Exception as e:
            return "Error when obtaining data from URL: " + url + "\n" + str(e)
    elif command.startswith("#"):
        return "Annotation: " + full_case[1:]
    else:
        return "Unknown command: //" + full_case + "//\n" + "The system uses a simple command line. If issuing a command, start with the command, followed by a space, and then the command parameters as described. Please ensure that you did not miss any spaces and are using the correct format."

def now():
    return datetime.now(timezone.utc).strftime("%A %d/%m/%Y %H:%M")
