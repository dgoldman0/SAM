from generation import generate_prompt
from generation import call_openai
import asyncio
import data
import dreams

# External dialogue

async def converse(name, socket):
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
                well_formed = False
                while not well_formed:
                    # Merge internal memory into conversation memory.
                    prompt = generate_prompt("merge", (data.memory_internal, data.memory, ))
                    merged_memory = call_openai(prompt, 2700)

                    # Use merged memory to generate conversation response.
                    prompt = generate_prompt("respond", (merged_memory, working_memory, name, message, ))
                    ai_response = call_openai(prompt, 128)
                    print("Response: " + ai_response + '\n')
                    # Integrate into conversation memory.
                    prompt = generate_prompt("integrate", (data.memory, working_memory, name, message, ai_response, ))
                    output = ""
                    while not output.endswith("END MEMORY"):
                        output = call_openai(prompt, 900)
                    data.memory = output.strip("END MEMORY")

                    # Integrate into internal memory.
                    prompt = generate_prompt("integrate", (data.memory_internal, working_memory, name, message, ai_response, ))
                    output = ""
                    while not output.endswith("END MEMORY"):
                        output = call_openai(prompt, 1800)
                    data.memory_internal = output.strip("END MEMORY")

                    prompt = generate_prompt("logic/well_formed", (ai_response, ))
                    response = call_openai(prompt, 32)
                    if response.lower().startswith("yes"):
                        well_formed = True
                working_memory += name + ": " + message + "\n\n"
                working_memory += "<ME>: " + ai_response + "\n\n"

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