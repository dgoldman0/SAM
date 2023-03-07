from generation import generate_prompt
from generation import call_openai
import asyncio
import data
import dreams
import utils
import parameters

server = None

def init(server_module):
    global server
    server = server_module

async def push_msg(user, message):
    username = user['username']
    socket = user['websocket']
    working_memory = data.get_workingmen(username)
    prompt = generate_prompt("internal/integrate", (data.memory, working_memory, ": " + message, ))
    await asyncio.get_event_loop().run_in_executor(None, utils.updateConversational, prompt)
    working_memory += ": " + message + "\n\n"
    data.set_workingmem(to, working_memory)
    await socket.send(("MSG:" + message).encode())

# External dialogue
async def converse(name, socket):
    global server
    # Need to persist working memory for each user across disconnects.
    connected = True
    while connected:
        if not data.locked:
            data.locked = True
            working_memory = data.get_workingmen(name)
            try:
                msg = (await socket.recv()).decode()
                if data.check_dreaming():
                    await socket.send(("STATUS: Sam is sleeping.").encode())
                elif msg.startswith("MSG:"):
                    message = msg[4:]
                    print("Received message: " + message + '\n')
                    # Merge internal memory into conversation memory, if conversation memory isn't blank
                    merged_memory = data.memory_internal
                    if data.memory != "":
                        prompt = generate_prompt("merge", (data.memory_internal, data.memory, ))
                        merged_memory = call_openai(prompt, parameters.internal_capacity + parameters.conversation_capacity)

                    # Use merged memory to generate conversation response.
                    prompt = generate_prompt("respond", (merged_memory, working_memory, name, message, ))
                    ai_response = call_openai(prompt, 128)
                    print("Response: " + ai_response + '\n')
                    await socket.send(("MSG:" + ai_response).encode())

                    if data.memory != "":
                        # Integrate into conversation memory, if it is not blank, otherwise create new base conversation
                        prompt = generate_prompt("integrate", (data.memory, working_memory, name, message, ai_response, ))
                        await asyncio.get_event_loop().run_in_executor(None, utils.updateConversational, prompt)
                    else:
                        prompt = generate_prompt("bootstrap", (data.memory_internal, name, message, ai_response, ))
                        data.memory = call_openai(prompt, parameters.conversation_capacity)
                    # Integrate into internal memory.
                    prompt = generate_prompt("integrate", (data.memory_internal, working_memory, name, message, ai_response, ))
                    await asyncio.get_event_loop().run_in_executor(None, utils.updateInternal, prompt)

                    working_memory += name + ": " + message.replace('\n', '\n\t') + "\n\n"
                    working_memory += ": " + ai_response.replace('\n', '\n\t') + "\n\n"

                    # Cut last line of old memory.
                    lines = working_memory.split('\n\n')

                    if len(lines) > 20:
                        lines = lines[1:]
                        working_memory = '\n\n'.join(lines)
                    data.set_workingmem(name, working_memory)
                    data.save()
                elif msg.startswith('COMMAND:'):
                    command = msg[8:]
                    if message == "memory":
                        await socket.send(("STATUS:" + data.memory).encode())
                    elif message == "working":
                        await socket.send(("STATUS:" + working_memory).encode())
                    elif message == "dream":
                        dreams.dream()
                else:
                    pass
            except Exception as e:
                print(e)
                connected = False
                server.notify_disconnect(name)
            data.locked = False
            await asyncio.sleep(0.1)
        await asyncio.sleep(0)
