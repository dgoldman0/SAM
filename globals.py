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
def save(physiology):
    global history, sub_history, database
    cur = database.cursor()
    res = cur.execute("UPDATE SYSTEM SET saved = 1, resource_credits = ?, history = ?;", (physiology.resource_credits, history))
    for i in range(physiology.max_partitions):
        res = cur.exeute("UPDATE SUBHISTORIES SET history = ? WHERE partition = ?;", (sub_history[i], i))
    database.commit()
# Will save and close gracefully.
def quit(physiology):
    save(physiology)
    sys.exit(0)

def load(physiology):
    global history, sub_history, resource_credits, database
    cur = database.cursor()
    res = cur.execute("SELECT saved, resource_credits, history FROM SYSTEM;")
    resp = res.fetchone()
    if (resp[0] == 1):
        physiology.resource_credits = resp[1]
        history = resp[2]
        res = cur.execute("SELECT history FROM SUBHISTORIES ORDER BY partition;")
        resp = res.fetchall()
        for entry in resp:
            total_partitions += 1
            sub_history.append(entry)
