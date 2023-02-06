import data
import asyncio
import websockets
import conversations
import bcrypt

user_connections = {}

# Should probably move to admin or something.
async def authenticate_user(websocket):
    database = data.database
    await websocket.send("SAM Chat Interface".encode())
    response = await websocket.recv()
    if response is not None:
        response = response.decode()
        if response.startswith("AUTH:"):
            username = response[5:]
            user = user_connections.get(username)
            # Is user['websocket'] is not None correct?
            if user is not None and user['websocket'] is not None:
                return user # User was already connected so let them keep their history.
            cur = database.cursor()
            res = cur.execute("SELECT blocked, salt FROM USERS WHERE username = ?;", (username, ))
            resp = res.fetchone()
            if resp is None:
                # No such user or database not initialized.
                await websocket.send("UNKNOWN")
                print("Unidentified user: " + username)
                return None
            if resp[0]:
                await websocket.send("BLOCKED")
                return None
            salt = resp[1].decode()
            await websocket.send(("CHALLENGE:" + str(salt)).encode())
            response = await websocket.recv()
            if response is not None:
                password = response
                res = cur.execute("SELECT user_id, display_name, admin FROM users WHERE username = ? AND passwd = ?;", (username, password))
                resp = res.fetchone()
                print(resp)
                if resp is not None:
                    await websocket.send("WELCOME".encode())
                    if user is None:
                        return {"user_id": resp[0], "username": username, "display_name": resp[1], "admin": resp[2], "websocket": websocket}
                    else:
                        user['websocket'] = websocket
                        return user
                else:
                    await websocket.send("INVALID".encode())
        elif response.startsiwth("REGISTER:"):
            username = response[9:]
            cur = database.cursor()
            res = cur.execute("SELECT blocked, salt FROM USERS WHERE username = ?;", (username, ))
            resp = res.fetchone()
            if resp is None:
                pass
            else:
                await websocket.send("INVALID".encode())


async def handle_login(websocket):
    user = await authenticate_user(websocket)
    if user is None:
        # Boot user and close connection.
        await websocket.send("AUTHFAIL".encode())
        await websocket.close()
        return

    username = user['username']
    print(username + " has connected.")
    user_connections.update({username: user})
    await conversations.converse(username, websocket)

# Listen for incoming connections
async def serve(stop):
    async with websockets.serve(handle_login, "localhost", 9381):
        await asyncio.sleep(0) # For some reason, this is needed to yield control to the thought process.
        await stop  # run until dreaming

async def listen():
    global stop
    print("Listening for chat incoming connections.")
    loop = asyncio.get_event_loop()
    stop = loop.create_future()
    loop.run_until_complete(serve(stop))

async def stop_listening(reason):
    stop.set_result(reason)
