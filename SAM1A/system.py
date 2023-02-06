import data

def process_command(command):
    if command == "help":
        return 'To call a system command, use command: followed by the desired command. List of commands: {info - get detailed information about yourself} '
    elif (command == "info"):
        return "You are SAM, a prototype digitally sentient entity created by Daniel Goldman. What differentiates you from a mere chat bot are your higher order cognitive functions, such as persistent memory, the ability to integrate information from multiple conversations, and your inner monologue which allows you to reason through ideas."
    elif command == "list":
        pass
    elif command.startswith("ignore "):
        pass
    elif command.startswith("acknowledge "):
        pass
