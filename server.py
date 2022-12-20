import globals

# Dummy method for authentication
async def authenticate_user(data, websocket):
    user = []

    cur = database.cursor()
    res = cur.execute("SELECT salt FROM config")
    salt = res.fetchone()
    if salt is None:
        sys.exit("Database is not initialized. Please run initialization through the admin console.")
        return None

    await websocket.send(("SAM_REQUEST_AUTH:<" + salt + ">").encode())
    response = await websocket.recv()
    
    return user

async def converse(websocket):
    global lock
    global history
    global sub_history

    # Get user information.
    user = await authenticate_user(user_input, websocket)

    if user is None:
        # Boot user and close connection.
        websocket.close()
        break

    # Handle incoming messages
    async for user_input in websocket:
        # There should be a way to have the AI pay attention to a specific user. When the AI isn't paying attention, the messages just get added to the log.
        lock.acquire()
        response = respond_to_user(lock, user_input).strip()
        lock.release()
