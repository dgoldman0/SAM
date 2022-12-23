import globals
import asyncio
import websockets
import thoughts
from threading import Thread

async def authenticate_user(websocket):
    database = globals.database
    await websocket.send("SAM Chat Interface".encode())
    response = await websocket.recv()

    if response is not None:
        response = response.decode()
        if response.startswith("AUTH:"):
            username = response[5:]
            cur = database.cursor()
            res = cur.execute("SELECT salt FROM USERS WHERE username = ?;", (username, ))
            resp = res.fetchone()
            if resp is None:
                # No such user or database not initialized.
                print("Unidentified user: " + username)
                return None
            salt = resp[0].decode()
            await websocket.send(("CHALLENGE:" + str(salt)).encode())
            response = await websocket.recv()
            if response is not None:
                password = response
                res = cur.execute("SELECT user_id, display_name, admin FROM users WHERE username = ? AND passwd = ?;", (username, password))
                resp = res.fetchone()
                if resp is not None:
                    await websocket.send("WELCOME".encode())
                    return {"user_id": resp[0], "username": username, "display_name": resp[1], "admin": resp[2]}

# Engage in active conversation with user.
async def converse(websocket):
    lock = globals.lock
    print("New Chat Connection")
    # Get user information.
    user = await authenticate_user(websocket)

    if user is None:
        # Boot user and close connection.
        print("User Unable to Validate")
        await websocket.send("AUTHFAIL".encode())
        websocket.close()
        return

    print("Authentication Success. Waiting for messages...")
    # Handle incoming messages
    async for user_input in websocket:
        # User will only "notice" and respond to the current active user (the person they're paying attention to), and the response will instead be generated by the subconscious.
        try:
            user_input = user_input.decode()
            lock.acquire()
            response = thoughts.respond_to_user(user["username"], user_input).strip()
            lock.release()
            await websocket.send(response.encode())
        except Exception as err:
            print(err)

# Listen for incoming connections
async def serve(stop):
    async with websockets.serve(converse, "localhost", 9381):
        await stop  # run until dreaming

async def listen():
    global stop
    print("Listening for chat incoming connections.")
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    stop = loop.create_future()
    loop.run_until_complete(serve(stop))

async def stop_listening(reason):
    stop.set_result(reason)
