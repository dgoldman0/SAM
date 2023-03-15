import io
import sqlite3
import nest_asyncio
import bcrypt
from generation import generate_prompt
from generation import call_openai
import parameters

# Connect to local file database which will be used to store user information, etc. Maybe one day replace with full MySQL
print("Connecting to database.")

# Load database and check for previous system history. That way we don't have to go through the whole bootup process each time, and if the system goes out at one pont it can be rebooted where it was left off.
database = sqlite3.connect("sam.db", check_same_thread=False)

nest_asyncio.apply()

dreaming = False

first = True

# Needed because some threading is necessary otherwise the websocket client won't work right
locked = False

# Working memories for each user conversation, stored in case of disconnects.
working_memory = {}
# Working memories conscious and subconscious layers
working_memories = []

# Need to update these to store and access from database
def getConversationWorkingMen(name):
    global working_memory
    return working_memory.get(name, '')

def setConversationWorkingMen(name, memory):
    global working_memory
    working_memory[name] = memory

def appendHistory(mem_id, history):
    global database
    cur = database.cursor()
    cur.execute("INSERT INTO HISTORY (mem_id, memory) VALUES (?, ?);", (mem_id, history, ))
    database.commit()

def appendMemory(memory):
    global database
    cur = database.cursor()
    cur.execute("INSERT INTO INTERNALMEM (memory) VALUES (?);", (memory, ))
    database.commit()

def getMemory(mem_id):
    global database
    cur = database.cursor()
    res = cur.execute("SELECT memory FROM INTERNALMEM WHERE mem_id = ?;", (mem_id, ))
    resp = res.fetchone()
    if resp is not None:
        return resp[0]
    return None;

def setMemory(mem_id, memory):
    global database
    cur = database.cursor()
    res = cur.execute("UPDATE INTERNALMEM SET memory = ? WHERE mem_id = ?;", (memory, mem_id, ))
    database.commit()

def memoryCount():
    global database
    cur = database.cursor()
    res = cur.execute("SELECT Count(mem_id) FROM INTERNALMEM;")
    return res.fetchone()[0]

def appendWorkingMemory(memory):
    global database
    cur = database.cursor()
    try:
        cur.execute("INSERT INTO INTERNALWMEM (memory) VALUES (?);", (memory, ))
    except Exception as e:
        print(e)
    database.commit()

def getWorkingMemory(mem_id):
    global database
    cur = database.cursor()
    res = cur.execute("SELECT memory FROM INTERNALWMEM WHERE mem_id = ?;", (mem_id, ))
    resp = res.fetchone()
    if resp is not None:
        return resp[0]
    return None;

def setWorkingMemory(mem_id, memory):
    global database
    cur = database.cursor()
    res = cur.execute("UPDATE INTERNALWMEM SET memory = ? WHERE mem_id = ?;", (memory, mem_id, ))
    database.commit()

def workingMemoryCount():
    global database
    cur = database.cursor()
    res = cur.execute("SELECT Count(mem_id) FROM INTERNALWMEM;")
    return res.fetchone()[0]

def set_dreaming(value):
    global dreaming
    dreaming = value

def check_dreaming():
    global dreaming
    return dreaming

# Load persistenet memory and initialize database of it does not exist yet.
def init():
    global database, memory, memory_internal
    try:
        cur = database.cursor()
        res = cur.execute("SELECT TRUE FROM USERS WHERE username = ?;", ("admin", ))
    except Exception as err:
        if str(err) == "no such table: USERS":
            # Create user table and add the administrator.
            cur.execute("CREATE TABLE USERS(user_id INT PRIMARY KEY, username TEXT NOT NULL, display_name TEXT NOT NULL, passwd TEXT NOT NULL, salt TEXT NOT NULL, admin INT DEFAULT FALSE, blocked NOT NULL DEFAULT FALSE);")
            username = input("Enter admin username: ")
            salt = bcrypt.gensalt()
            admin_password = "not"
            confirm = "same"
            while confirm != admin_password:
                admin_password = input("Enter admin password: ")
                confirm = input("Confirm password: ")
            password = bcrypt.hashpw(admin_password.encode(), salt)
            cur.execute("INSERT INTO USERS (username, display_name, passwd, salt, admin) VALUES (?, ?, ?, ?, ?);", (username, "System Administrator", password, salt, True))
            # Create internal memory table. mem_id = 0 is conscious, and all others are subconscious layers
            cur.execute("CREATE TABLE INTERNALMEM(mem_id INTEGER PRIMARY KEY NOT NULL, memory TEXT DEFAULT '');");
            # Create persistent memory history
            cur.execute("CREATE TABLE HISTORY(hist_id INTEGER PRIMARY KEY NOT NULL, mem_id INT NOT NULL, memory TEXT NOT NULL DEFAULT '')")
            # User memory
            cur.execute("CREATE TABLE USERMEM(mem_id INTEGER PRIMARY KEY NOT NULL, username TEXT UNIQUE NOT NULL, memory TEXT DEFAULT '');")

            # Create internal working memory table. mem_id = 0 is conscious as before.
            cur.execute("CREATE TABLE INTERNALWMEM(mem_id INTEGER PRIMARY KEY NOT NULL, memory TEXT DEFAULT '');");
            # User working memory
            cur.execute("CREATE TABLE USERWMEM(mem_id INTEGER PRIMARY KEY NOT NULL, username TEXT UNIQUE NOT NULL, memory TEXT DEFAULT '');")
            database.commit()

            # Initialize memory
            print("Bootstrapping memory...")
            prompt = generate_prompt("membootstrap", (parameters.features, ))
            memory_internal = call_openai(prompt, 1550, temp = 0.9)
            appendMemory(memory_internal)
            appendHistory(1, memory_internal)

            prompt = generate_prompt("internal/bootstrap_working", (memory_internal, ))
            bootstrap = call_openai(prompt, 128, temp = 0.85).replace('\n', '\n\t')
            appendWorkingMemory(bootstrap)

            for i in range(parameters.subs):
                print("Bootstrapping subconscious(" + str(i) + ")...")
                prompt = generate_prompt("internal/bootstrap_working", (memory_internal, ))
                bootstrap = call_openai(prompt, 128, temp = 0.95)
                appendWorkingMemory(bootstrap)
            print("Finished initializing database...\n\n")
        else:
            raise Exception("Unknown Error")

# Stub for training feature. Will train and then update the model info
def train(pairs):
    pass
