# An administration interface for the system

import data
import bcrypt
import physiology

def initialize_database(admin_password):
    database = data.database
    # Check if already initialized
    cur = database.cursor()
    try:
        res = cur.execute("SELECT TRUE FROM USERS WHERE username = ?;", ("admin", ))
        raise Exception("Already initialized")
    except Exception as err:
        if str(err) == "no such table: USERS":
            # Create user table and add the administrator.
            cur.execute("CREATE TABLE USERS(user_id INT PRIMARY KEY, username TEXT NOT NULL, display_name TEXT NOT NULL, passwd TEXT NOT NULL, salt TEXT NOT NULL, admin INT DEFAULT FALSE, credits INT NOT NULL DEFAULT 0, blocked NOT NULL DEFAULT FALSE);")
            salt = bcrypt.gensalt()
            password = bcrypt.hashpw(admin_password.encode(), salt)
            cur.execute("INSERT INTO USERS (username, display_name, passwd, salt, admin) VALUES (?, ?, ?, ?, ?);", ("admin", "System Administrator", password, salt, True))
            cur.execute("INSERT INTO USERS (username, display_name, passwd, salt, admin) VALUES (?, ?, ?, ?, ?);", ("daniel", "System Administrator II", password, salt, True))
            cur.execute("CREATE TABLE SYSTEM(saved INT NOT NULL DEFAULT 0, resource_credits INT NOT NULL DEFAULT 0, history TEXT NOT NULL DEFAULT '');")
            cur.execute("CREATE TABLE SUBHISTORIES(partition INT NOT NULL, history TEXT NOT NULL DEFAULT '');")
            # Fill system and subhistory tables with blank data.
            database.execute("INSERT INTO SYSTEM(saved) VALUES(0);")
            for i in range (physiology.max_partitions):
                database.execute("INSERT INTO SUBHISTORIES(partition) VALUES(" + str(i) + ");")
            database.commit()
        else:
            raise Exception("Unknown Error")


def block_user(username):
    database = data.database
    cur = database.cursor()
    cur.execute("UPDATE USERS SET blocked = TRUE WHERE username = ?", (username, ))
    database.commit()

def unblock_user(username):
    database = data.database
    cur = database.cursor()
    cur.execute("UPDATE USERS SET blocked = FALSE WHERE username = ?", (username, ))
    database.commit()
