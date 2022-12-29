import globals
import thoughts
import server
import admin
import monitoring
import asyncio
import physiology
from sqlite3 import OperationalError
from threading import Thread

# Future version should start thinking about a new information integration function where new information is integrated. But that would require more training which is expensive.
# I have System Notifications. Now I need System Commands to get the AI to control things.

# Want to be able to include an offline history so the bot can talk to the users while they're offline. Though not what kind of code to get the bot to do that.

database = data.database

cur = database.cursor()

try:
    res = cur.execute("SELECT TRUE FROM USERS WHERE username = ?;", ("admin", ))
except OperationalError as err:
    if str(err) == "no such table: USERS":
        print("System is not yet initialized. Preparing system now.")
        password = ""
        while True:
            password = input("Choose admin password: ")
            password_repeat = input("Confirm password: ")
            if password == password_repeat:
                break
            # Repeat until the passwords match.
            print("Passwords do not match. Please try again.")
        print("Adding administrator information to database.")
        admin.initialize_database(password)
    else:
        raise Exception("Unknown Error")

async def main():
    await asyncio.gather(thoughts.boot_ai(), server.listen())

data.load(thoughts, physiology)
asyncio.run(main())
