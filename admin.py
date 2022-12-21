# An administration interface for the system

import globals
def initialize_database(admin_password):
    database = globals.database
    # Check if already initialized
    cur = database.cursor()
    res = cur.execute("SELECT TRUE FROM USERS WHERE username = '%s';", ("admin", ))
    if res is not None:
        raise Exception("Already initialized")

    # Create user table and add the administrator.
    cur.execute("CREATE TABLE USERS(user_id INT NOT NULL AUTO_INCREMENT, username varchar(15) NOT NULL, display_name varchar(30) NOT NULL, password VARCHAR(255) NOT NULL, salt VARCHAR(255) NOT NULL, admin BOOL DEFAULT FALSE) PRIMARY KEY(user_id)")
    salt = bcrypt.getsalt()
    password = bcrypt.hashpw(admin_password, salt)
    cur.execute("INSERT INTO USERS (username, password, salt, admin) VALUES ('%s', '%s', '%s', '%s');", ("admin", "System Administrator", salt, password))

    # Create rest of database...
