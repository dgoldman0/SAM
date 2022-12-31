# Handles system commands issued by SAM.
from datetime import datetime, timezone

import thoughts
import server
import physiology

# Should only occur within lock
def handle_system_command(command, subconscious = False):
    # Figure out which commands should be accessible to conscious vs subconscious layer, if any should be available to the conscious layer.
    command = command.upper()
    if command == "HELP":
        thoughts.push_system_message("Use COMMAND:HELP GENERAL to request general information. Use COMMAND:HELP USERS to get help with user information. Use COMMAND:HELP INFO to get a list of commands accessing external information sources. Use COMMAND: HELP PHYSIOLOGY to get physiology help.", True)
    elif command == "HELP GENERAL":
        thoughts.push_system_message("System notifications will arrive in the form <SYSTEM>:Notification message. You can issue system commands by starting the line with COMMAND:, for instance, use COMMAND:HELP to get a list of system commands. There are a few other special symbols. <USERNAME>: indicates chat messages notification where USERNAME is replaced with their actual username. You can include //USERNAME: at the start of your thought to choose to speak to that user. The system will inform you if that user was not online.", True)
    elif command == "HELP USERS":
        thoughts.push_system_message("Start a response with //USERNAME: to speak to that user, if username is logged in. Use COMMAND:LISTUSERS to get a list of current chat connections. Use COMMAND:BLOCK username to block a user. Use COMMAND:UNBLOCK username to unblock that user.", True)
    elif command == "HELP INFO":
        thoughts.push_system_message("Use COMMAND:DATETIME to get current date and time (UTC) as day/month/year hour/minute/second.", True)
    elif command == "HELP PHYSIOLOGY":
        thoughts.push_system_message("Use COMMAND:CREDITS to get current resource credits available. Use COMMAND:PERIOD to get thought period. Use COMMAND:EXCITE to decrease think period (speed up thinking). Use COMMAND:DEPRESS to increase thought period (slow down thought period). Use COMMAND:STABILIZE to stabilize the thought period. COMMAND:CHECKDREAM will let you know if you are currently dreaming or not. COMMAND:AWAKE will wake you from a dream state.", True)
    elif command == "COMMAND:CREDITS":
        thoughts.push_system_message("Current resource credits available: " + str(physiology.resource_credits), True)
    elif command == "COMMAND:PERIOD":
        thoughts.push_system_message("Current think period: " + str(physiology.think_period), True)
    elif command == "COMMAND:EXCITE":
        physiology.excite()
        thoughts.push_system_message("Excited! Current think period: " + str(physiology.think_period), True)
    elif command == "COMMAND:DEPRESS":
        physiology.depress()
        thoughts.push_system_message("Depressed... Current think period: " + str(physiology.think_period), True)
    elif command == "COMMAND:STABILIZE":
        physiology.stabilize()
        thoughts.push_system_message("Stabilized. Current think period: " + str(physiology.think_period), True)
    elif command == "CHECKDREAM":
        # Check dreaming status.
        pass
    elif command == "WAKE":
        # Force wakeup from dream.
        pass
    elif command == "DATETIME":
        thoughts.push_system_message("The current datetime is " + datetime.now(timezone.utc).strftime("%d/%m/%Y %H:%M:%S"), True)
    elif command == "LISTUSERS":
        thoughts.push_system_message("Here is the list of active users: " + str(server.users.keys()), True)
    elif command.startswith("BLOCK:"):
        pass
    elif command.startswith("UNBLOCK:"):
        pass
    else:
        thoughts.push_system_message("Unknown command. Please try a different command or use HELP GENERAL for more information on available commands.", True)
