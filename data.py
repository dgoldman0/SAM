# Global variables

# Import modules that will be needed elsewhere
import sys
import sqlite3
from threading import Lock
import nest_asyncio

first_load = True

# The history between active user and Sam, as well as the direct inner dialog.
history = ""
history_tuples = []
# History between inner voice and subconscious, to be replaced with an array of histories.
sub_history = []
sub_history_tuples = []
total_partitions = 0

# Connect to local file database which will be used to store user information, etc. Maybe one day replace with full MySQL
print("Connecting to database.")

# Load database and check for previous system history. That way we don't have to go through the whole bootup process each time, and if the system goes out at one pont it can be rebooted where it was left off.
database = sqlite3.connect("sam.db")

nest_asyncio.apply()

# Will save the current state.
def save(physiology):
    try:
        global total_partitions, history, sub_history, database
        cur = database.cursor()
        # Continue to add system state information from physiology
        print("History: " + history)
        res = cur.execute("UPDATE SYSTEM SET saved = 1, resource_credits = ?, history = ?;", (physiology.resource_credits, history))
        for i in range(total_partitions):
            res = cur.execute("UPDATE SUBHISTORIES SET history = ? WHERE partition = ?;", (sub_history[i], i))
        database.commit()
    except Exception as err:
        print(err)

# Will save and close gracefully.
def quit(physiology):
    save(physiology)
    sys.exit(0)

def load(thoughts, physiology):
    global total_partitions, history, sub_history, resource_credits, database, first_load
    cur = database.cursor()
    res = cur.execute("SELECT saved, resource_credits, history FROM SYSTEM;")
    resp = res.fetchone()
    if (resp[0] == 1):
        first_load = False
        physiology.resource_credits = resp[1]
        history = resp[2]
        res = cur.execute("SELECT history FROM SUBHISTORIES ORDER BY partition;")
        resp = res.fetchall()
        for entry in resp:
            total_partitions += 1
            sub_history.append(entry[0])
