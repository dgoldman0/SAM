import globals
import asyncio
import websockets
import thoughts
import monitoring
from threading import Thread

user_connections = {}

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
                    return {"user_id": resp[0], "username": username, "display_name": resp[1], "admin": resp[2], "websocket": websocket}

# Push a messaage to an active user.
async def message_user(username, message):
    user = user_connections.get(username)
    if user is not None:
        await user['websocket'].send(message)
    else:
        # Notify SAM that no user is present.
        thoughts.push_system_message(username + " is not logged in.")

# Engage in active conversation with user.
async def converse(websocket):
    lock = globals.lock
    # Get user information.
    user = await authenticate_user(websocket)
    username = user['username']
    user_connections.update({username: user})
    if user is None:
        # Boot user and close connection.
        await websocket.send("AUTHFAIL".encode())
        websocket.close()
        return

    # Monitoring won't push notifications until after a chat connects.
    globals.lock.acquire()
    monitoring.notify_new_chat(username)
    thoughts.push_system_message(username + " connected.")
    globals.lock.release()

    # Handle incoming messages: need to figure out how to handle disconnects.
    try:
        async for user_input in websocket:
            # User will only "notice" and respond to the current active user (the person they're paying attention to), and the response will instead be generated by the subconscious.
            user_input = user_input.decode()
            lock.acquire()
            response = thoughts.respond_to_user(username, user_input).strip()
            lock.release()
            try:
                await websocket.send(response.encode())
            except websockets.ConnectionClosed as exc:
                # Connection closed. Notify system and delete.
                globals.lock.acquire()
                monitoring.notify_chat_closed(username)
                thoughts.push_system_message(username + " disconnected.")
                globals.lock.release()
                del user_connections[user['username']]
    except Exception as err:
        print(err)
# Listen for incoming connections
async def serve(stop):
    async with websockets.serve(converse, "localhost", 9381):
        await stop  # run until dreaming

async def listen():
    global stop
    print("Listening for chat incoming connections.")
    loop = asyncio.get_event_loop()
    stop = loop.create_future()
    loop.run_until_complete(serve(stop))

async def stop_listening(reason):
    stop.set_result(reason)
