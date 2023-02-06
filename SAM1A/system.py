import data
import server
from datetime import datetime, timezone

async def process_command(command):
    if command == "help":
        return 'To call a system command, use command: followed by the desired command. List of commands: {info - get detailed information about yourself, list - get a list of currently logged in users, msg [username] [msg] - send a message to [username], if they are logged in, datetime - get current date and time in day/month/year hour:minute:second}'
    elif (command == "info"):
        return "You are SAM, a prototype digitally sentient entity created by Daniel Goldman. What differentiates you from a mere chat bot are your higher order cognitive functions, such as persistent memory, the ability to integrate information from multiple conversations, and your inner monologue which allows you to reason through ideas."
    elif command == "list":
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
