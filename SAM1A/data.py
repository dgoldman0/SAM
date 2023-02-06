import io
import sqlite3
import nest_asyncio
import bcrypt

# Connect to local file database which will be used to store user information, etc. Maybe one day replace with full MySQL
print("Connecting to database.")

# Load database and check for previous system history. That way we don't have to go through the whole bootup process each time, and if the system goes out at one pont it can be rebooted where it was left off.
database = sqlite3.connect("sam.db")

nest_asyncio.apply()

memory = ""
memory_internal = ""

dreaming = False

# Working memories for each user conversation, stored in case of disconnects.
working_memory = {}

def get_workingmen(name):
    global working_memory
    return working_memory.get(name, '')

def set_workingmem(name, memory):
    global working_memory
    working_memory[name] = memory

def set_dreaming(value):
    global dreaming
    dreaming = value

def check_dreaming():
    global dreaming
    return dreaming

# Load persistenet memory and initialize database of it does not exist yet.
def init():
    global database
    # Check if already initialized
    cur = database.cursor()
    try:
        file = open('memory.txt',mode='r')
        memory = file.read()
        file.close()
        file = open('memory_internal.txt',mode='r')
        memory = file.read()
        file.close()
    except Exception as e:
        pass
    try:
        res = cur.execute("SELECT TRUE FROM USERS WHERE username = ?;", ("admin", ))
    except Exception as err:
        if str(err) == "no such table: USERS":
            # Create user table and add the administrator.
            cur.execute("CREATE TABLE USERS(user_id INT PRIMARY KEY, username TEXT NOT NULL, display_name TEXT NOT NULL, passwd TEXT NOT NULL, salt TEXT NOT NULL, admin INT DEFAULT FALSE, blocked NOT NULL DEFAULT FALSE);")
            salt = bcrypt.gensalt()
            admin_password = "not"
            confirm = "same"
            while confirm != admin_password:
                admin_password = input("Enter admin password: ")
                confirm = input("Confirm password: ")
            password = bcrypt.hashpw(admin_password.encode(), salt)
            cur.execute("INSERT INTO USERS (username, display_name, passwd, salt, admin) VALUES (?, ?, ?, ?, ?);", ("admin", "System Administrator", password, salt, True))
            database.commit()
        else:
            raise Exception("Unknown Error")

# Save persistent memory.
def save():
    try:
        file = open('memory.txt',mode='w')
        file.write(memory)
        file.close()
        file = open('memory_internal.txt',mode='w')
        file.write(memory_internal)
        file.close()
    except Exception as e:
        print(e)
