# An administration interface for the system

import globals
import bcrypt

def initialize_database(admin_password):
    database = globals.database
    # Check if already initialized
    cur = database.cursor()
    res = None
    try:
        res = cur.execute("SELECT TRUE FROM USERS WHERE username = ?;", ("admin", ))
        raise Exception("Already initialized")
    except Exception as err:
        if str(err) == "no such table: USERS":
            # Create user table and add the administrator.
            cur.execute("CREATE TABLE USERS(user_id INT PRIMARY KEY, username TEXT NOT NULL, display_name TEXT NOT NULL, passwd TEXT NOT NULL, salt TEXT NOT NULL, admin INT DEFAULT FALSE);")
            salt = bcrypt.gensalt()
            password = bcrypt.hashpw(admin_password.encode(), salt)
            cur.execute("INSERT INTO USERS (username, display_name, passwd, salt, admin) VALUES (?, ?, ?, ?, ?);", ("admin", "System Administrator", password, salt, True))
            database.commit()
            # Create rest of database...
        else:
            raise Exception("Unknown Error")
