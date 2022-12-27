import asyncio
import websockets
import bcrypt
import time

username = None
hashed_pw = None

# Very simple websocket client that was used for initial testing, but does not wait for incoming messages.

async def connect():
    global username
    global hashed_pw
    async with websockets.connect('ws://localhost:9381') as websocket:
        print("Connecting to service...")
        response = await websocket.recv()
        if response is not None and response.decode() == "SAM Chat Interface":
            if username is None:
                username = input("Connected. Please enter username: ")
            await websocket.send(("AUTH:" + username).encode())
            response = await websocket.recv()
            if response is not None:
                response = response.decode()
                if response.startswith("CHALLENGE:"):
                    salt = response[10:]
                    if hashed_pw is None:
                        password = input("Enter password: ")
                        hashed_pw = bcrypt.hashpw(password.encode(), salt.encode())
                    await websocket.send(hashed_pw)
                    response = await websocket.recv()
                    if response is not None:
                        if response.decode() == "WELCOME":
                            print("Connection established! Please enjoy chatting with SAM.")
                            message = input("<" + username + ">: ")
                            # This system needs to be replaced with one where it waits for incoming messages regardless of whether the user has sent anything.
                            while message != "/quit":
                                await websocket.send(message.encode())
                                response = await websocket.recv()
                                if response is not None:
                                    print("<SAM>: " + response.decode())
                                    message = input("<" + username + ">: ")
                        else:
                            username = None
                            hashed_pw = None
                            print("Authentication Failed. Try again...")
        return

async def main():
    while True:
        try:
            await connect()
        except Exception as err:
            print("Disconnected, trying again.")
        time.sleep(5)
asyncio.run(main())
