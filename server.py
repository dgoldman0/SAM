import data
import asyncio
import websockets
import thoughts
import monitoring
import learning

from threading import Thread

max_user_tips = 10000
user_connections = {}

async def authenticate_user(websocket):
    database = data.database
    await websocket.send("SAM Chat Interface".encode())
    response = await websocket.recv()
    if response is not None:
        response = response.decode()
        if response.startswith("AUTH:"):
            username = response[5:]
            user = user_connections.get(username)
            if user is not None and user['websocket'] is not None:
                return user # User was already connected so let them keep their history.
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
                print(resp)
                if resp is not None:
                    await websocket.send("WELCOME".encode())
                    if user is None:
                        return {"user_id": resp[0], "username": username, "display_name": resp[1], "admin": resp[2], "websocket": websocket, "history": "", "history_tuples": [], "tokens_spent": 0, "tips": 0}
                    else:
                        user['websocket'] = websocket
                        return user

# Push a messaage to a user. Since this message is not coming as a reply, it is tagged with "//"
async def message_user(username, message):
    user = user_connections.get(username)
    if user is not None:
        user['history'] += "\n//" + message
        await user['websocket'].send(("MSG:" + message).encode())
    else:
        # Notify SAM that no user is present.
        thoughts.push_system_message(username + " is not logged in.")

# Engage in active conversation with user.
async def converse(websocket):
    # Get user information.
    user = await authenticate_user(websocket)
    if user is None:
        # Boot user and close connection.
        await websocket.send("AUTHFAIL".encode())
        websocket.close()
        return

    username = user['username']
    print(username + " has connected.")
    user_connections.update({username: user})
    # Might not be a good idea. I dunno.
    thoughts.active_user = username
    # Monitoring won't push notifications until after a chat connects.
    monitoring.notify_new_chat(username)
    thoughts.push_system_message(username + " connected.")

    # Handle incoming messages: need to figure out how to handle disconnects.
    try:
        async for user_input in websocket:
            # User will only "notice" and respond to the current active user (the person they're paying attention to), and the response will instead be generated by the subconscious.
            user_input = user_input.decode()
            response = "I'm still waking up..."
            # Should add a notification in the chat history that the user tipped. Also want to create a safeguard preventing users from tricking the system into thinking that a tip was added. Same with other things like voiced messages. Maybe by keeping it encoded.
            if user_input.startswith("MSG:"):
                # If not waking up still, process message.
                if not thoughts.waking_up:
                    response = thoughts.respond_to_user(user, user_input[4:])
                try:
                    await websocket.send(("MSG:" + response).encode())
                except Exception:
                    # Connection closed. Notify system and delete.
                    monitoring.notify_chat_closed(username)
                    thoughts.push_system_message(username + " disconnected.")
                    user_connections[user['username']]['websocket'] = None
            elif user_input.startswith("COMMAND:"):
                # Process command such as save state. This code should go in its own function, but for now this is fine.
                command = user_input[8:].upper()
                if (command == "SAVE"):
                    # Save current state.
                    if user['admin']:
                        data.save()
                        await websocket.send("STATUS:System saving...".encode())
                    else:
                        await websocket.send("STATUS:Insufficient Authority.".encode())
                elif command == "CLOSE":
                    # Save and close down the system.
                    if user['admin']:
                        await websocket.send("STATUS:System shutting down...".encode())
                        data.quit()
                    else:
                        await websocket.send("STATUS:Insufficient Authority.".encode())
                elif command == "DAYDREAM":
                    if user['admin']:
                        await websocket.send("STATUS:System entering daydream...".encode())
                        await learning.daydream()
                    else:
                        await websocket.send("STATUS:Insufficient Authority.".encode())
                elif command.startswith("TIP "):
                    try:
                        tip = int(command[4:])
                        if user['tips'] + tip < max_user_tips:
                            user['tips'] += tip
                            user['history'] += "<SYSTEM>:User tipped " + str(tip)
                            await websocket.send("STATUS:Tipped successfully.".encode())
                        else:
                            await websocket.send("STATUS:Insufficient balance.".encode())
                    except Exception as err:
                        print("ERR: " + err)
                        await websocket.send("STATUS:Invalid tip amount.".encode())
                else:
                    await websocket.send("STATUS:Unknown command.".encode())
    except Exception as err:
        print(err)

# Listen for incoming connections
async def serve(stop):
    async with websockets.serve(converse, "localhost", 9381):
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
