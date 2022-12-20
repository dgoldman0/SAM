import asyncio
import websockets
import openai
import sys
import logging
import random
import time
from threading import Thread
from threading import Lock

# Future version should start thinking about a new information integration function where new information is integrated. But that would require more training which is expensive.
# I have System Notifications. Now I need System Commands to get the AI to control things.

# Want to be able to include an offline history so the bot can talk to the users while they're offline. Though not what kind of code to get the bot to do that.

# Final version will have different models for conscious dialog and subconscious partitions.
#conscious = "davinci:ft-personal-2022-12-14-17-05-26" # includes both general knoweldge and concept connections
# Eventually each subconscious partition might run on a different model.
#subconscious = "davinci:ft-personal-2022-12-14-17-05-26" # includes both general knoweldge and concept connections

# Good to test code with the super cheap basic models, at least to check for errors.
conscious = "davinci"
subconscious = "davinci" 

# Full history of all thinking
full_history = ""

# The history between user and Sam, as well as the direct inner dialog. This will have to become a list because of multiple conversations.
history = ""

# History between inner voice and subconscious, to be replaced with an array of histories.
sub_history = []

# Generate a subconscious thought and propogate to a conscious thought
def step_subconscious(partition, lock):
    global history
    global sub_history
    global full_history
    # Get next completion from the subconscious based on existing subconscious dialogue.
    next_prompt = openai.Completion.create(
        model=subconscious,
        temperature=1,
        max_tokens=75,
        top_p=0.5,
        frequency_penalty=0.5f,
        presence_penalty=0.5,
        prompt=sub_history[partition] + "\n",
        stop="\n")["choices"][0]["text"].strip()
    sub_history[partition] = sub_history[partition] + "\nSubconscious: " + next_prompt
    full_history = full_history + "\n<Subconscious(" + partition + ")>: " + next_prompt
    # Get next completion for the conscious dialog, using subconscious history as the prompt (subconscious injecting itself into consciousness)
    next_prompt = openai.Completion.create(
        model=conscious,
        temperature=0.9,
        max_tokens=125,
        top_p=0.5,
        frequency_penalty=1,
        presence_penalty=1,
        prompt=sub_history[partition] + "\n",
        stop="\n")["choices"][0]["text"].strip()
    history = history + "\nConscious: " + next_prompt
    sub_history[partition] = sub_history[partition] + "\nConscious: " + next_prompt
    full_history = full_history + "\n<Conscious>: " + next_prompt

# One iteration of inner dialog. This method needs to be able to initiate communications with users so it needs websockets. Or it could use a log.
def step_conscious(lock):
    global history
    global sub_history
    global full_history
    next_prompt = openai.Completion.create(
        model=conscious,
        temperature=0.5,
        max_tokens=125,
        top_p=0.7,
        frequency_penalty=1,
        presence_penalty=1,
        prompt=history + "\n",
        stop="\n")["choices"][0]["text"].strip()
    # If the prompt starts with Sam,
    if (next_prompt.startswith("Sam:")):
        next_prompt = next_prompt.replace("Sam:", "").replace("User:", "").replace("Conscious:", "").replace("Subconscious:", "").strip()
        print("Sam: " + next_prompt)
        history = history + "\nSam: " + next_prompt
        full_history = full_history + "\n<Sam>: " + next_prompt
    else:
        history = history + "\nConscious: " + next_prompt
        partitions = len(sub_history)
        if partitions > 1:
            # Flip to see if the conscious thought should be added to the subconscious log.
            flip = random.randint(0, 1)
            if flip:
                partition = random.randint(0, partitions - 1)
                sub_history[partition] = sub_history[partition] + "\nConscious: " + next_prompt

        full_history = full_history + "\n<Conscious>: " + next_prompt

# This method is not set up for multiple users. That's a problem. In fact, it is not set up for websocket either.
def respond_to_user(lock, user_input):
    global history
    global sub_history
    global full_history
    history = history + "\nUser: " + user_input.strip()
    full_history = full_history + "\n<User>: " + user_input.strip()
    next_prompt = openai.Completion.create(
        model=conscious,
        temperature=0.4,
        max_tokens=250,
        top_p=1,
        frequency_penalty=1,
        presence_penalty=1,
        prompt=history + "\n",
        stop="\n")["choices"][0]["text"].replace("Sam:", "").replace("User:", "").replace("Conscious:", "").replace("Subconscious:", "").strip()

    history = history + "\nSam: " + next_prompt
    full_history = full_history + "\n<Sam>: " + next_prompt

    return next_prompt

# Inner dialog loop
def think(lock):
    global history
    while True:
        lock.acquire()
        step_conscious(lock)
        # Prevent the prompt from getting too long by cutting off old chat history
        if (len(history) > 5120):
            loc = history.index("\n")
            if (loc is not None):
                history = history[loc + 1:]
        lock.release()
        time.sleep(2)

# Subconscious to conscious interaction loops
def sub_think(partition, lock):
    global sub_history
    while True:
        lock.acquire()
        step_subconscious(partition, lock)
        # Prevent the prompt from getting too long by cutting off old chat history. Subconscious history is much shorter to keep it dynamic and save on computation.
        if (len(sub_history[partition]) > 500):
            loc = sub_history[partition].index("\n")
            if (loc is not None):
                sub_history[partition] = sub_history[partition][loc + 1:]
        lock.release()
        time.sleep(6)

lock = Lock()

# Need a connection and disconnection notice to let the AI know.

# Dummy method for authentication
async def authenticate_user(data, websocket):
    user = []
    return user

async def converse(websocket):
    global lock
    global history
    global sub_history
    first_message = True

    # User data
    user = []

    # Get user information.
    user = authenticate_user(user_input, websocket)
    if user is None:
        # Boot user and close connection.
        break

    # Handle incoming messages
    async for user_input in websocket:
        # There should be a way to have the AI pay attention to a specific user. When the AI isn't paying attention, the messages just get added to the log.
        lock.acquire()
        response = respond_to_user(lock, user_input).strip()
        lock.release()

# Bootup AI
def wake_ai():
    global history
    global lock

    # System notification to AI of wakeup. Should include various status information once I figure out what to include.
    print("AI Starting Up")
    startup_message = "System Notifications: Waking up."

    # Begin inner dialog
    t = Thread(target=think, args=[lock], daemon=True)
    print("Starting Inner Dialog")
    t.start()

    # Start three partitions of subconscious dialog after the user replies, one at a time.
    for partition in range(3):
        # Wait three seconds to start each partition to give time for inner dialog to propogate.
        time.sleep(3)
        t = Thread(target=sub_think, args=[partition, lock], daemon=True)
        print("Starting Subconscious Partition " + partition)
        t.start()

async def main():
    wake_ai()
    async with websockets.serve(converse, "localhost", 9381):
        await asyncio.Future()  # run forever

asyncio.run(main())
