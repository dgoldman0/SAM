# Global variables

# Import modules that will be needed elsewhere

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
database = sqlite3.connect("sam.db")

nest_asyncio.apply()
