# Global variables

# Import modules that will be needed elsewhere

import asyncio
import websockets
import openai
import logging
import random
import time
import bcrypt
from threading import Thread
from threading import Lock
import sqlite3

# The history between active user and Sam, as well as the direct inner dialog.
history = ""

# History between inner voice and subconscious, to be replaced with an array of histories.
sub_history = []

# Connect to local file database which will be used to store user information, etc. Maybe one day replace with full MySQL
print("Connecting to database.")
database = sqlite3.connect("sam.db")

lock = Lock()
