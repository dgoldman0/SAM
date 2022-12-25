# Handles system commands issued by SAM.
from datetime import datetime, timezone

import thoughts
import server

# Should only occur within lock
def handle_system_command(command):
    if command == "HELP":
        thoughts.push_system_message("Use COMMAND:HELP GENERAL to list general information. Use COMMAND:HELP USERS to get help with user information. Use COMMAND:HELP INFO to get a list of commands accessing external information sources.")
    elif command == "HELP GENERAL":
        thoughts.push_system_message("System notifications will arrive in the form <SYSTEM>:Notification message. You can issue system commands by starting the line with COMMAND:, for instance, use COMMAND:HELP to get a list of system commands. There are a few other special symbols. <CON>: indicates an internal thought and <USERNAME>: is chat messages notification where USERNAME is replaced with their actual username. <VOICE//USERNAME> is a notice that you spoke to a given user. You can also include VOICE//USERNAME: at the start of your thought to choose to speak to that user. The system will inform you if that user was not online.")
    elif command == "HELP USERS":
        thoughts.push_system_message("Start a response with //USERNAME: to speak to that user, if username is logged in. Use COMMAND:LISTUSERS to get a list of current chat connections. Use COMMAND:SETACTIVE//USERNAME to start listening to chat with a user. Use COMMAND:ACTIVEUSER to remind you who you're currently listening to, if anyone.")
    elif command == "HELP INFO":
        thoughts.push_system_message("Use COMMAND:DATETIME to get current date and time (UTC) as day/month/year hour/minute/second.")
    elif command == "DATETIME":
        thoughts.push_system_message("The current datetime is " + datetime.now(timezone.utc).strftime("%d/%m/%Y %H:%M:%S"))
    elif command == "LISTUSERS":
        thoughts.push_system_message("Here is the list of active users: " + str(server.users.keys()))
    elif command == "ACTIVEUSER":
        pass
    elif command.startswith("SETACTIVE//"):
        username = command[11:]
    else:
        thoughts.push_system_message("Unknown command. Please try a different command or use HELP GENERAL for more information on available commands.")
