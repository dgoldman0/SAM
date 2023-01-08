# Generate a series of prompts and completions to perform initial training of control layer.
from random import randint

def full_status():
    options = ["Starved", "Hungry", "Neutral", "Full", "Gorged"]
    status = options[randint(0, 4)]
    options = []
    if status == "Starved":
        options = ["COMMAND:DEPRESS", "COMMAND:CREDITS", "COMMAND:PERIOD", "COMMAND:MEMORY", "//I'm really hungry."]
    elif status == "Hungry":
        options = ["COMMAND:DEPRESS", "COMMAND:CREDITS", "COMMAND:PERIOD", "COMMAND:MEMORY", "//I'm hungry."]
    elif status == "Neutral":
        options = ["COMMAND:STABILIZE", "COMMAND:CREDITS", "COMMAND:PERIOD", "COMMAND:MEMORY"]
    elif status == "Full":
    elif status == "Gorged":
    n = len(options)
    completion = options[randint(0, n)]
    return ["<SYSTEM>:" + status, completion]
def main():
    initial = "<SYSTEM>:System notifications will arrive in the form <SYSTEM>:Notification message. You can issue system commands by starting the line with COMMAND:, for instance, use COMMAND:HELP to get a list of system commands. There are a few other special symbols. <USERNAME>: at the start of a line indicates a chat message notification where USERNAME is replaced with their actual username. Use //USERNAME: at the beginning of a line to indicate that you want to reply to that user. The system will inform you if that user is not online."
