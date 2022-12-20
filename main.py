import asyncio
import websockets
import openai
import logging
import random
import time
from threading import Thread
from threading import Lock

import globals
import thoughts
import sleep

# Future version should start thinking about a new information integration function where new information is integrated. But that would require more training which is expensive.
# I have System Notifications. Now I need System Commands to get the AI to control things.

# Want to be able to include an offline history so the bot can talk to the users while they're offline. Though not what kind of code to get the bot to do that.

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
