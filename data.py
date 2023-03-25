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

thinking = False #temp

# Working memory for conversation. Should be put in DB soon.
working_memory = ""

# Channel Functions
def getChannelList():
    global database
    cur = database.cursor()
    res = cur.execute("SELECT channel_id FROM CHANNELS;")
    resp = res.fetchall()
    if resp is not None:
        return resp
    return None

# Returns a list of users (usernames) in a channel
def getChannelUsers(channel_id):
    global database
    cur = database.cursor()
    res = cur.execute("SELECT username FROM CHANNELS WHERE channel_id = ?;", (channel_id, ))
    resp = res.fetchall()
    if resp is not None:
        return resp
    return None

def getUserChannelList(user_id):
    global database
    cur = database.cursor()
    res = cur.execute("SELECT channel_id FROM CHANNELS WHERE user_id = ?;", (user_id, ))
    resp = res.fetchall()
    if resp is not None:
        return resp
    return None

def userInChannel(user_id, channel_id):
    global database
    cur = database.cursor()
    res = cur.execute("SELECT channel_id FROM CHANNELS WHERE user_id = ? AND channel_id = ?;", (user_id, channel_id, ))
    resp = res.fetchone()
    if resp is not None:
        return True
    return False

def joinChannel(user_id, channel_id):
    global database
    cur = database.cursor()
    res = cur.execute("INSERT INTO CHANNELS (user_id, channel_id) VALUES (?, ?);", (user_id, channel_id, ))
    database.commit()

def leaveChannel(user_id, channel_id):
    global database
    cur = database.cursor()
    res = cur.execute("DELETE FROM CHANNELS WHERE user_id = ? AND channel_id = ?;", (user_id, channel_id, ))
    database.commit()

# Memory Functions
def getChannelWorkingMem(channel_id):
    global database
    cur = database.cursor()
    res = cur.execute("SELECT memory FROM INTERNALWMEM WHERE channel_id = ?;", (channel_id, ))
    resp = res.fetchone()
    if resp is not None:
        return resp[0]
    return None

def setChannelWorkingMem(channel_id, memory):
    global database
    cur = database.cursor()
    res = cur.execute("UPDATE INTERNALWMEM SET memory = ? WHERE channel_id = ?;", (memory, channel_id, ))
    database.commit()
    
def appendChannelHistory(channel_id, mem_id, history):
    global database
    cur = database.cursor()
    cur.execute("INSERT INTO HISTORY (channel_id, mem_id, memory) VALUES (?, ?, ?);", (channel_id, mem_id, history, ))
    database.commit()

def appendChannelMemory(channel_id, memory):
    global database
    cur = database.cursor()
    cur.execute("INSERT INTO INTERNALMEM (channel_id, memory) VALUES (?, ?);", (channel_id, memory, ))
    database.commit()

def getChannelMemory(channel_id, mem_id):
    global database
    cur = database.cursor()
    res = cur.execute("SELECT memory FROM INTERNALMEM WHERE channel_id = ? AND mem_id = ?;", (channel_id, mem_id, ))
    resp = res.fetchone()
    if resp is not None:
        return resp[0]
    return None

def setChannelMemory(channel_id, mem_id, memory):
    global database
    cur = database.cursor()
    res = cur.execute("UPDATE INTERNALMEM SET memory = ? WHERE channel_id = ? AND mem_id = ?;", (memory, channel_id, mem_id, ))
    database.commit()

def channelMemoryCount(channel_id):
    global database
    cur = database.cursor()
    res = cur.execute("SELECT Count(mem_id) FROM INTERNALMEM WHERE channel_id = ?;", (channel_id, ))
    return res.fetchone()[0]

def appendChannelWorkingMemory(channel_id, memory):
    global database
    cur = database.cursor()
    try:
        cur.execute("INSERT INTO INTERNALWMEM (channel_id, memory) VALUES (?, ?);", (channel_id, memory, ))
    except Exception as e:
        print(e)
    database.commit()

def getChannelWorkingMemory(channel_id, mem_id):
    global database
    cur = database.cursor()
    res = cur.execute("SELECT memory FROM INTERNALWMEM WHERE channel_id = ? AND mem_id = ?;", (channel_id, mem_id, ))
    resp = res.fetchone()
    if resp is not None:
        return resp[0]
    return None

def setChannelWorkingMemory(channel_id, mem_id, memory):
    global database
    cur = database.cursor()
    res = cur.execute("UPDATE INTERNALWMEM SET memory = ? WHERE channel_id = ? AND mem_id = ?;", (memory, channel_id, mem_id, ))
    database.commit()

def channelWorkingMemoryCount(channel_id):
    global database
    cur = database.cursor()
    res = cur.execute("SELECT Count(mem_id) FROM INTERNALWMEM WHERE channel_id = ?;", (channel_id, ))
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
            # Create user citations table for moderation citations issued in a given channel.
            cur.execute("CREATE TABLE USERCITATIONS(citation_id INTEGER PRIMARY KEY NOT NULL, user_id INT NOT NULL, channel_id INT NOT NULL, citation TEXT NOT NULL, citation_date DATETIME DEFAULT CURRENT_TIMESTAMP);")    
            
            username = input("Enter admin username: ")
            salt = bcrypt.gensalt()
            admin_password = "not"
            confirm = "same"
            while confirm != admin_password:
                admin_password = input("Enter admin password: ")
                confirm = input("Confirm password: ")
            password = bcrypt.hashpw(admin_password.encode(), salt)
            cur.execute("INSERT INTO USERS (username, display_name, passwd, salt, admin) VALUES (?, ?, ?, ?, ?);", (username, "System Administrator", password, salt, True))
            cur.execute("CREATE TABLE CHANNELS(channel_id INTEGER PRIMARY KEY NOT NULL, name TEXT NOT NULL, description TEXT NOT NULL);")
            cur.execute("INSERT INTO CHANNELS (name, description) VALUES ('general', 'General Chat');")
            cur.execute("CREATE TABLE CHANNELMEMBERS(channel_id INT NOT NULL, user_id INT NOT NULL, admin INT DEFAULT FALSE);")
            cur.execute("INSERT INTO CHANNELMEMBERS (channel_id, user_id, admin) VALUES (1, 1, TRUE);")
            # Create internal memory table. mem_id = 0 is conscious, and all others are subconscious layers
            cur.execute("CREATE TABLE INTERNALMEM(mem_id INTEGER PRIMARY KEY NOT NULL, channel_id INT NOT NULL, memory TEXT DEFAULT '');")
            # Create persistent memory history
            cur.execute("CREATE TABLE HISTORY(hist_id INTEGER PRIMARY KEY NOT NULL, channel_id INT NOT NULL, mem_id INT NOT NULL, memory TEXT NOT NULL DEFAULT '')")
            # User memory
            cur.execute("CREATE TABLE USERMEM(mem_id INTEGER PRIMARY KEY NOT NULL, username TEXT UNIQUE NOT NULL, memory TEXT DEFAULT '');")

            # Create internal working memory table. mem_id = 0 is conscious as before.
            cur.execute("CREATE TABLE INTERNALWMEM(mem_id INTEGER PRIMARY KEY NOT NULL, channel_id INT NOT NULL, memory TEXT DEFAULT '');")
            # Channel working memory
            cur.execute("CREATE TABLE USERWMEM(mem_id INTEGER PRIMARY KEY NOT NULL, channel_id INT NOT NULL, memory TEXT DEFAULT '');")
            database.commit()

            # Initialize memory
            print("Bootstrapping memory...")
            # Bootstrap with a slightly smaller initial profile.
            prompt = generate_prompt("membootstrap", (parameters.features, utils.internalLength() * 0.8, ))
            memory_internal = call_openai(prompt, parameters.internal_capacity, temp = 0.9, model = "gpt-4")
            appendChannelMemory(1, memory_internal)
            appendChannelHistory(1, 1, memory_internal)

            prompt = generate_prompt("internal/bootstrap_working", (memory_internal, ))
            bootstrap = call_openai(prompt, 128, temp = 0.85).replace('\n', '\n\t')
            appendChannelWorkingMemory(1, bootstrap)
            # Blank for conversation memory
            appendChannelWorkingMemory(1, "")
            # Seed subconscious partition workig memories
            for i in range(parameters.subs):
                print("Bootstrapping subconscious(" + str(i) + ")...")
                prompt = generate_prompt("internal/bootstrap_working", (memory_internal, ))
                bootstrap = call_openai(prompt, 128, temp = 0.95)
                appendChannelMemory(1, "")
                appendChannelWorkingMemory(1, bootstrap)
            print("Finished initializing database...\n\n")
        else:
            raise Exception("Unknown Error")

# Stub for training feature. Will train and then update the model info
def train(pairs):
    pass
