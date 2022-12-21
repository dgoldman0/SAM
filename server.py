import globals

# Dummy method for authentication
async def authenticate_user(data, websocket):
    global database
    response = await websocket.recv()

    # Format of response should be AUTH:[username]
    if response is not None:
        response = response.decode()
        split = response.index("&")
        if split is not None:
            command = response[:split]
            if command == "AUTH":
                username = response[split + 1:]
                cur = database.cursor()
                res = cur.execute("SELECT salt FROM USERS WHERE username = %s;", (username, ))
                resp = res.fetchone()
                if resp is None:
                    # No such user or database not initialized.
                    return None
                salt = resp[0]
                password = await websocket.send(("CHALLENGE:" + salt).encode())
                resp = cur.execute("SELECT user_id, display_name FROM users WHERE username = %s AND password = %s;", (username, password))
                if res is not None:
                    # For now just returns username, and user_id, but should include more data I think.
                    return {'username': username, 'user_id': res[0], 'display_name': res[1]}

# Engage in active conversation with user.
async def converse(websocket):
    lock = globals.lock

    # Get user information.
    user = await authenticate_user(user_input, websocket)

    if user is None:
        # Boot user and close connection.
        websocket.close()
        return

    # Handle incoming messages
    async for user_input in websocket:
        # There should be a way to have the AI pay attention to a specific user. When the AI isn't paying attention, the messages just get added to the log.
        lock.acquire()
        response = thoughts.respond_to_user(user_input).strip()
        websocket.send(("SAM: " + response).encode())
        lock.release()

# Listen for incoming connections
async def _listen(stop):
    async with websockets.serve(converse, "localhost", 9381):
        await stop  # run forever

async def listen():
    global stop
    print("Listening for incoming connections.")
    loop = asyncio.get_event_loop()
    stop = loop.create_future()
    loop.run_until_complete(_listen(stop))

async def stop_listening(reason):
    stop.set_result(reason)
