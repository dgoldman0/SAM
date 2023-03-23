import io
import sqlite3
import nest_asyncio
import bcrypt
import asyncio
from generation import generate_prompt
from generation import call_openai
import parameters
import utils

# Connect to local file database which will be used to store user information, etc. Maybe one day replace with full MySQL
print("Connecting to database.")

# Load database and check for previous system history. That way we don't have to go through the whole bootup process each time, and if the system goes out at one pont it can be rebooted where it was left off.
database = sqlite3.connect("collab.db", check_same_thread=False)

nest_asyncio.apply()

dreaming = False

first = True

thinking = True

# Working memory for conversation. Should be put in DB soon.
working_memory = ""

def getConversationWorkingMem():
    global working_memory
    return working_memory

def setConversationWorkingMem(memory):
    global working_memory
    working_memory = memory

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
            # Teams will be included in later versions. Internal memory, working memory, history, etc. will be tied to a team ID
            cur.execute("CREATE TABLE TEAMS(team_id INTEGER PRIMARY KEY NOT NULL, name TEXT NOT NULL, description TEXT NOT NULL);")
            cur.execute("CREATE TABLE TEAMUSERS(team_id INT NOT NULL, user_id INT NOT NULL);")
            cur.execute("INSERT INTO TEAMS (name, description) VALUES ('admins', 'Administration Core Team');")
            cur.execute("INSERT INTO TEAMUSERS (team_id, user_id) VALUES (1, 1);")
            # Create internal memory table. mem_id = 0 is conscious, and all others are subconscious layers
            cur.execute("CREATE TABLE INTERNALMEM(mem_id INTEGER PRIMARY KEY NOT NULL, memory TEXT DEFAULT '');")
            # Create persistent memory history
            cur.execute("CREATE TABLE HISTORY(hist_id INTEGER PRIMARY KEY NOT NULL, mem_id INT NOT NULL, memory TEXT NOT NULL DEFAULT '')")
            # User memory
            cur.execute("CREATE TABLE USERMEM(mem_id INTEGER PRIMARY KEY NOT NULL, username TEXT UNIQUE NOT NULL, memory TEXT DEFAULT '');")

            # Create internal working memory table. mem_id = 0 is conscious as before.
            cur.execute("CREATE TABLE INTERNALWMEM(mem_id INTEGER PRIMARY KEY NOT NULL, memory TEXT DEFAULT '');")
            # User working memory
            cur.execute("CREATE TABLE USERWMEM(mem_id INTEGER PRIMARY KEY NOT NULL, team TEXT UNIQUE NOT NULL, memory TEXT DEFAULT '');")
            database.commit()

            # Initialize memory
            print("Bootstrapping memory...")
            # Bootstrap with a slightly smaller initial profile.
            prompt = generate_prompt("membootstrap", (parameters.features, utils.internalLength() * 0.8, ))
            memory_internal = call_openai(prompt, utils.internal_capacity, temp = 0.9, model = "gpt-4")
            appendMemory(memory_internal)
            appendHistory(1, memory_internal)

            prompt = generate_prompt("internal/bootstrap_working", (memory_internal, ))
            bootstrap = call_openai(prompt, 128, temp = 0.85).replace('\n', '\n\t')
            appendWorkingMemory(bootstrap)
            # Blank for conversation memory
            appendWorkingMemory("")
            # Seed subconscious partition workig memories
            for i in range(parameters.subs):
                print("Bootstrapping subconscious(" + str(i) + ")...")
                prompt = generate_prompt("internal/bootstrap_working", (memory_internal, ))
                bootstrap = call_openai(prompt, 128, temp = 0.95)
                appendMemory("")
                appendWorkingMemory(bootstrap)
            print("Finished initializing database...\n\n")
        else:
            raise Exception("Unknown Error")

# Stub for training feature. Will train and then update the model info
def train(pairs):
    pass
