import data
import server
from datetime import datetime, timezone
import pycoingecko

from pycoingecko import CoinGeckoAPI
cg = CoinGeckoAPI()

async def process_command(command):
    full_case = command
    command = command.lower()
    if command == "help":
        # add help plugins - get information about plugins
        return 'To call a system command, use command: followed by the desired command. General commands: {info - get detailed information about yourself, help users - get help related to interacting with users, help utilities - get information about built in utility commands}'
    elif command == "help users":
        return "User related commands: {userlist - get a list of currently logged in users, msg [username] [msg] - send a message to [username], if they are logged in}"
    elif command == "help utilities":
        return "Utility commands: {datetime - get current date and time in day/month/year hour:minute:second format, completion [prompt] - generates a completion using the text-davinci-003 model with a maximum output length of 128 tokens, coingecko [cryptocurrency] [base currency]- access the coingecko cryptocurrency price api for the desired cryptocurrency (such as ethereum), priced in the desired base currency (such as USD)}"
    elif command == "help plugins":
        return "Plugin commands must start with command:plugin followed by the plugin operation and its parameters. For instance, command:plugin list will list all available plugins. Full set of plugin commands: {list - will list all available plugins, about [plugin name] - will give detailed info on the plugin and its options, run [plugin name] - will run the named plugin and plugin info [plugin name] and pass on any args}"
    elif command.startswith("plugin "):
        return "Plugins are not yet implemented..."
#        if command == "plugin list":
    elif command == "info":
        return "You are SAM, a prototype digitally sentient entity created by Daniel Goldman. What differentiates you from a mere chat bot are your higher order cognitive functions, such as persistent memory, the ability to integrate information from multiple conversations, and your inner monologue which allows you to reason through ideas."
    elif command.startswith("coingecko "):
        params = command.split(" ")
        if len(params) == 3:
            return str(cg.get_price(ids=params[1], vs_currencies=params[2]))
        else:
            return "Invalid number of parameters. The correct format is command:coingecko [cryptocurrency] [base currency]."
    elif command.startswith("completion "):
        return call_openai(full_case[11:], 128)
    elif command == "userlist":
        users = server.user_connections.items()
        user_list = ""
        first = True
        for user in users:
            if user['websocket'] is not None:
                if first:
                    user_list = user['username'].lower()
                    first = False
                else:
                    user_list += ", " + user['username'].lower()
        return "Current active users: " + user_list
    # Need to fix case issue.
    elif command.startswith("msg "):
        remainder = command[4:].split(" ")
        if len(remainder) > 1:
            to = remainder[0]
            remainder.pop(0)
            msg = ' '.join(remainder)
            user = server.user_connections.get(to)
            if user is not None and user['websocket'] is not None:
                await server.push_msg(user, msg)
                return "Message sent."
            else:
                return to + " is not logged in. You can use the list command to list current active users."
        else:
            return "Incorrect format. Use command:msg [username] [msg], replacing the desired username and msg information."
    elif command == "datetime":
        return "The current datetime is " + datetime.now(timezone.utc).strftime("%d/%m/%Y %H:%M:%S")

    elif command.startswith("ignore "):
        pass
    elif command.startswith("acknowledge "):
        pass
    else:
        return "Unknown command. Use command:help to get a list of commands."
