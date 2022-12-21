import globals
import thoughts
import server
import admin
from sqlite3 import OperationalError

# Future version should start thinking about a new information integration function where new information is integrated. But that would require more training which is expensive.
# I have System Notifications. Now I need System Commands to get the AI to control things.

# Want to be able to include an offline history so the bot can talk to the users while they're offline. Though not what kind of code to get the bot to do that.

database = globals.database

async def main():
    await thoughts.wake_ai()
    await server.listen()

cur = database.cursor()
try:
    res = cur.execute("SELECT TRUE FROM USERS WHERE username = '%s';", ("admin", ))
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

# Run main
asyncio.run(main())
