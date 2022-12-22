import globals
import asyncio

async def authenticate_user(data, websocket):
    database = globals.database
    await websocket.send("SAM Chat Interface".encode())
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
                res = cur.execute("SELECT salt FROM USERS WHERE username = ?;", (username, ))
                resp = res.fetchone()
                if resp is None:
                    # No such user or database not initialized.
                    return None
                salt = resp[0]
                password = await websocket.send(("CHALLENGE:" + salt).encode()).decode()
                resp = cur.execute("SELECT user_id, display_name FROM users WHERE username = ? AND passwd = ?;", (username, password))
                if res is not None:
                    # For now just returns username, and user_id, but should include more data I think.
                    return {'username': username, 'user_id': res[0], 'display_name': res[1]}
