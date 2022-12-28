# Global variables

# Import modules that will be needed elsewhere
import sys
import sqlite3
from threading import Lock
import nest_asyncio

# The history between active user and Sam, as well as the direct inner dialog.
history = ""

# History between inner voice and subconscious, to be replaced with an array of histories.
sub_history = []

#lock = Lock()

# Connect to local file database which will be used to store user information, etc. Maybe one day replace with full MySQL
print("Connecting to database.")

# Load database and check for previous system history. That way we don't have to go through the whole bootup process each time, and if the system goes out at one pont it can be rebooted where it was left off.
database = sqlite3.connect("sam.db")

nest_asyncio.apply()

# Will save the current state.
async def save():
    pass

# Will save and close gracefully.
async def quit):
    await save()
    sys.exit(0)
