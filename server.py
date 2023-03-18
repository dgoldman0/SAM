import data
import asyncio
import websockets
import conversations
import bcrypt
import internal

user_connections = {}
connections = 0

def handleDisconnect(name):
    global connections
    global user_connections
    connections -= 1
    del user_connections[name]

# Should probably move to admin or something.
async def authenticateUser(websocket):
    database = data.database
    await websocket.send("SAM Collaboration System".encode())
    response = await websocket.recv()
    if response is not None:
        response = response.decode()
        if response.startswith("AUTH:"):
            # Username is always lowercase on the server end.
            username = response[5:].lower()
            cur = database.cursor()
            res = cur.execute("SELECT blocked, salt FROM USERS WHERE username = ?;", (username, ))
            resp = res.fetchone()
            if resp is None:
                # No such user or database not initialized.
                await websocket.send("UNKNOWN")
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


async def handleLogin(websocket):
    global connections
    user = await authenticateUser(websocket)
    if user is None:
        # Boot user and close connection.
        await websocket.send("AUTHFAIL".encode())
        await websocket.close()
        return

    username = user['username']
    user_connections.update({username: user})
    connections += 1
    await sendMessage("STATUS:" + username + " has connected.", user['websocket'])
    await conversations.converse(username, websocket)

async def sendMessage(message, excluded = None):
    for user in user_connections.values():
        socket = user['websocket']
        if socket != excluded:
            await socket.send(message.encode())

# Listen for incoming connections
async def serve(stop):
    async with websockets.serve(handleLogin, "localhost", 9381):
        await asyncio.sleep(0) # For some reason, this is needed to yield control to the thought process.
        await stop

async def listen():
    global stop
    print("Listening for chat incoming connections.")
    loop = asyncio.get_event_loop()
    stop = loop.create_future()
    loop.run_until_complete(serve(stop))

async def stop_listening(reason):
    stop.set_result(reason)
