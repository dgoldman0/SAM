import asyncio
import websockets
import bcrypt

async def main():
    async with websockets.connect('ws://localhost:9381') as websocket:
        print("Connecting to service...")
        response = await websocket.recv()
        if response is not None and response.decode() == "SAM Chat Interface":
            username = input("Connected. Please enter username: ")
            await websocket.send(("AUTH:" + username).encode())
            response = await websocket.recv()
            if response is not None:
                response = response.decode()
                if response.startswith("CHALLENGE:"):
                    salt = response[10:]
                    password = input("Enter password: ")
                    hashed_pw = bcrypt.hashpw(password.encode(), salt.encode())
                    await websocket.send(hashed_pw)
                    response = await websocket.recv()
                    if response is not None:
                        if response.decode() == "WELCOME":
                            print("Connection established! Please enjoy chatting with SAM.")
                            message = input("<" + username + ">: ")
                            while message != "/quit":
                                await websocket.send(message.encode())
                                response = await websocket.recv()
                                if response is not None:
                                    print("<SAM>: " + response.decode())
                                    message = input("<" + username + ">: ")
                        else:
                            print("Authentication Failed. Try again...")
        return
asyncio.run(main())
