# Handles system commands issued by SAM.
from datetime import datetime, timezone

import thoughts
import server
import physiology
import learning
import admin

help_prompt = "<SYSTEM>:System notifications will arrive in the form <SYSTEM>:Notification message. You can issue system commands by starting the line with COMMAND:, for instance, use COMMAND:HELP to get a list of system commands. There are a few other special symbols. <USERNAME>: at the start of a line indicates a chat message notification where USERNAME is replaced with their actual username. Use //USERNAME: at the beginning of a line to indicate that you want to reply to that user. The system will inform you if that user is not online."

def credits():
    return round(100 * physiology.resource_credits / physiology.resource_credits_full)

def period():
    return round(100 * (physiology.think_period - physiology.min_think_period) / (physiology.max_think_period - physiology.min_think_period))

# Should only occur within lock
def handle_system_command(command, subconscious = False):
    # Figure out which commands should be accessible to conscious vs subconscious layer, if any should be available to the conscious layer.
    command = command.upper()
    print("Command Executed: " + command)
    if command == "HELP":
        thoughts.push_system_message("Use COMMAND:HELP GENERAL to request general information. Use COMMAND:HELP USERS to get help with user information. Use COMMAND:HELP INFO to get a list of commands accessing external information sources. Use COMMAND:HELP PHYSIOLOGY to get physiology help.", True)
    elif command == "HELP GENERAL":
        thoughts.push_system_message("System notifications will arrive in the form <SYSTEM>:Notification message. You can issue system commands by starting the line with COMMAND:, for instance, use COMMAND:HELP to get a list of system commands. There are a few other special symbols. <USERNAME>: indicates chat messages notification where USERNAME is replaced with their actual username. You can include //USERNAME: at the start of your thought to choose to speak to that user. The system will inform you if that user was not online.", True)
    elif command == "HELP USERS":
        thoughts.push_system_message("Start a response with //USERNAME: to speak to that user, if username is logged in. Use COMMAND:LISTUSERS to get a list of current chat connections. Use COMMAND:BLOCK username to block a user. Use COMMAND:UNBLOCK username to unblock that user.", True)
    elif command == "HELP INFO":
        thoughts.push_system_message("Use COMMAND:DATETIME to get current date and time (UTC) as day/month/year hour/minute/second.", True)
    elif command == "HELP PHYSIOLOGY":
        thoughts.push_system_message("Use COMMAND:CREDITS to get current resource credits available. Use COMMAND:PERIOD to get thought period. Use COMMAND:EXCITE to decrease think period (speed up thinking). Use COMMAND:DEPRESS to increase thought period (slow down thought period). Use COMMAND:STABILIZE to stabilize the thought period. COMMAND:CHECKDREAM will let you know if you are currently dreaming or not. COMMAND:AWAKE will wake you from a dream state.", True)
    elif command == "CREDITS":
        # Might change this to a percentage. Same with Period.
        thoughts.push_system_message("Current resource credits available: " + str(credits()), True)
    elif command == "PERIOD":
        thoughts.push_system_message("Current think period: " + str(period()), True)
    elif command == "EXCITE":
        physiology.excite()
        thoughts.push_system_message("Excited! Current think period: " + str(physiology.think_period), True)
    elif command == "DEPRESS":
        physiology.depress()
        thoughts.push_system_message("Depressed... Current think period: " + str(physiology.think_period), True)
    elif command == "STABILIZE":
        physiology.stabilize()
        thoughts.push_system_message("Stabilized. Current think period: " + str(physiology.think_period), True)
    elif command == "CHECKDREAM":
        # Check dreaming status.
        if learning.dream_state == "Dreaming":
            thoughts.push_system_message("Currently asleep.", True)
        else:
            thoughts.push_system_message("Currently awake.", True)
    elif command == "WAKE":
        learning.dream_state = "Awake"
        thoughts.push_system_message("Forced wakeup started.", True)
    elif command == "DATETIME":
        thoughts.push_system_message("The current datetime is " + datetime.now(timezone.utc).strftime("%d/%m/%Y %H:%M:%S"), True)
    elif command == "LISTUSERS":
        thoughts.push_system_message("Here is the list of active users: " + str(server.users.keys()), True)
    elif command.startswith("BLOCK:"):
        username = command[6:]
        if len(username) > 0:
            admin.block(username)
            thoughts.push_system_message("User was blocked by request.", True)
    elif command.startswith("UNBLOCK:"):
        username = command[6:]
        if len(username) > 0:
            admin.unblock(username)
            thoughts.push_system_message("User was unblocked by request.", True)
    else:
        thoughts.push_system_message("Unknown command. Please try a different command or use HELP GENERAL for more information on available commands.", True)
