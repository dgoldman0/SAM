from generation import generate_prompt
from generation import call_openai
import asyncio
import data
import dreams

server = None

def init(server_module):
    global server
    server = server_module

async def push_msg(user, message):
    username = user['username']
    socket = user['websocket']
    working_memory = data.get_workingmen(username)
    prompt = generate_prompt("internal/integrate", (data.memory, working_memory, "<ME>: " + message, ))
    output = ""
    while not output.endswith("END MEMORY"):
        output = call_openai(prompt, parameters.conversation_capacity)
    data.memory = output.strip("END MEMORY")
    working_memory += "<ME>: " + message + "\n\n"
    data.set_workingmem(to, working_memory)
    await socket.send(("MSG:" + message).encode())

# External dialogue
async def converse(name, socket):
    global server
    # Need to persist working memory for each user across disconnects.
    connected = True
    while connected:
        working_memory = data.get_workingmen(name)
        try:
            msg = (await socket.recv()).decode()
            if data.check_dreaming():
                await socket.send(("STATUS: Sam is sleeping.").encode())
            elif msg.startswith("MSG:"):
                message = msg[4:]
                print("Received message: " + message + '\n')
                # Merge internal memory into conversation memory.
                prompt = generate_prompt("merge", (data.memory_internal, data.memory, ))
                merged_memory = call_openai(prompt, parameters.internal_capacity + parameters.conversation_capacity)

                # Use merged memory to generate conversation response.
                prompt = generate_prompt("respond", (merged_memory, working_memory, name, message, ))
                ai_response = call_openai(prompt, 128)
                print("Response: " + ai_response + '\n')

                # Integrate into conversation memory.
                prompt = generate_prompt("integrate", (data.memory, working_memory, name, message, ai_response, ))
                output = ""
                # Loop while malformed or there's a significant reduction in content length.
                while not output.endswith("END MEMORY") or len(output) < 0.95 * len(data.memory):
                    output = call_openai(prompt, parameters.conversation_capacity)
                data.memory = output.strip("END MEMORY")

                # Integrate into internal memory.
                prompt = generate_prompt("integrate", (data.memory_internal, working_memory, name, message, ai_response, ))
                output = ""
                # Loop while malformed or there's a significant reduction in content length.
                while not output.endswith("END MEMORY") or len(output) < 0.95 * len(data.memory_internal):
                    output = call_openai(prompt, parameters.internal_capacity)
                data.memory_internal = output.strip("END MEMORY")

                working_memory += name + ": " + '\n\t'.join(message.split('\n')) + "\n\n"
                working_memory += ": " + '\n\t'.join(ai_response.split('\n')) + "\n\n"

                # Cut last line of old memory.
                lines = working_memory.split('\n\n')

                if len(lines) > 20:
                    lines = lines[1:]
                    working_memory = '\n\n'.join(lines)
                data.set_workingmem(name, working_memory)
                await socket.send(("MSG:" + ai_response).encode())
            elif msg.startswith('COMMAND:'):
                command = msg[8:]
                if message == "memory":
                    await socket.send(("STATUS:" + data.memory).encode())
                elif message == "working":
                    await socket.send(("STATUS:" + working_memory).encode())
                elif message == "dream":
                    dreams.dream()
                elif message == "save":
                    data.save()
            else:
                pass
        except Exception as e:
            connected = False
            server.notify_disconnect(name)
