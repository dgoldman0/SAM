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
    global cg
    full_case = command
    command = command.lower()
    if command.startswith("respond "):
        server.sendMessage(full_case[8:])
        return "Responded with:" + full_case[8:]
    elif command.startswith("coingecko "):
        params = command.split(" ")
        if params[1] == "current":
            if len(params) == 4:
                if params[2].startswith('"') or params[3].startswith('"'):
                    return "There is no need for quotation marks for the COINGECKO command."
                else:
                    try:
                        return "Coingecko current price data: " + str(cg.get_price(ids=params[2], vs_currencies=params[3], include_market_cap='true', include_24hr_vol='true', include_24hr_change='true', include_last_updated_at='true'))
                    except Exception as e:
                        return "Coingecko API Error: " + str(e)
            else:
                return "Invalid number of parameters. The correct format is COINGECKO CURRENT [comma separated list of cryptocurrencies] [comma separated list of base currencies]. Avoid spaces in each list, but ensure a space between the two lists."
        elif params[1] == "24h":
            if len(params) == 4:
                    if params[2].startswith('"') or params[3].startswith('"'):
                        return "There is no need for quotation marks for the COINGECKO command."
                    else:
                        try:
                            return "Coingecko five day 24h volume and price history: " + str(cg.get_coin_market_chart_by_id(id=params[2],vs_currency=params[3],days='5'))
                        except Exception as e:
                            return "Coingecko API Error: " + str(e)
            else:
                return "Invalid number of parameters. The correct format is COINGECKO DAILY [comma separated list of cryptocurrencies] [comma separated list of base currencies]. Avoid spaces in each list, but ensure a space between the two lists."
        elif params[1] == "historical":
            if len(params) == 6:
                if params[2].startswith('"') or params[3].startswith('"') or params[4].startswith('"') or params[5].startswith('"'):
                    return "There is no need for quotation marks for the COINGECKO command."
                else:
                    try:
                        return "Coingecko historical price data: " + str(cg.get_coin_market_chart_range_by_id(id=params[2],vs_currency=params[3],from_timestamp=params[4],to_timestamp=params[5]))
                    except Exception as e:
                        return "Coingecko API Error: " + str(e)
        else:
            return "Unknown option for coingecko: " + params[1]
    elif command.startswith("tweepy "):
        params = command.split(" ")
        if params[1] == "followers":
            if len(params) == 3:
                return "Tweepy list of people following " + params[2] + ":\n" + twitter.userFollowers(params[2], None)
            elif len(params) == 4:
                return "Tweepy list of people following " + params[2] + " and next_token=" + params[3] + ":\n" + twitter.userFollowers(params[2], params[3])
            else:
                return "Invalid number of parameters. The correct format is TWEETPY FOLLOWERS [user] [next_token]."
        elif params[1] == "following":
            if len(params) == 3:
                return "Tweepy list of people following " + params[2] + ":\n" + twitter.userFollowing(params[2], None)
            elif len(params) == 4:
                return "Tweepy list of people following " + params[2] + " and next_token=" + params[3] + ":\n" + twitter.userFollowing(params[2], params[3])
            else:
                return "Invalid number of parameters. The correct format is TWEETPY FOLLOWING [user] [next_token]."
        elif params[1] == "user":
            if len(params) == 3:
                return "Tweepy user info for " + params[2] + ":\n" + twitter.userInfo(params[2])
            else:
                return "Invalid number of parameters. The correct format is TWEETPY USER [user]."
        elif params[1] == "search":
            if len(params) == 3:
                return "Tweepy recent search with parameters: " + params[2] + "\nResults:\n" + twitter.search(params[2])
            else:
                return "Invalid number of parameters. The correct format is TWEETPY SEARCH [json parameters]."
        elif params[1] == "timeline":
            if len(params) == 3:
                return "Tweepy timeline for user " + params[2] + ":\n" + twitter.userTimeline(params[2], None)
            elif len(params) == 4:
                return "Tweepy timeline for user " + params[2] + " and next_token=" + params[3] + ":\n" + twitter.userTimeline(params[2], params[3])
            else:
                return "Invalid number of parameters. The correct format is TWEETPY TIMELINE [user] [next_token]."
        elif params[1] == "tweet":
            message = full_case[13:]
            return "Tweepy tweet with message: " + message + "\nResults:\n" + twitter.tweet(message)
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
    elif command.startswith("input "):
        # Disabled right now but will need to add back command: INPUT [username] [query] - Ask a user a question and return their response
        params = full_case.split(' ')
        prompt = ' '.join(params[2:])
        try:
            await server.sendMessage("msg:" + prompt)
            user = server.user_connections.get(params[1])
            if user is not None:
                return "Input requested from " + params[1] + ": " + prompt + "\nResponse: " + (await user['websocket'].recv()).decode()
        except Exception as e:
            return "Exception while getting input: " + str(e)
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

if __name__ == '__main__':
    print(cg.get_coin_market_chart_by_id(id='ethereum',vs_currency='usd',days='3'))
