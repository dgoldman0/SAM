from generation import generate_prompt
from generation import call_openai
import asyncio
import data
import dreams
import utils
import parameters

server = None

# Alter code to have one single group chat.

def init(server_module):
    global server
    server = server_module

# External dialogue
async def converse(name, socket):
    global server
    # Need to persist working memory for each user across disconnects.
    connected = True
    while connected:
        await data.lock.acquire()
        working_memory = data.getConversationWorkingMem()
        memory = data.getMemory(1)
        try:
            msg = (await socket.recv()).decode()
            if msg.startswith("MSG:"):
                message = msg[4:]
                print("Received message: " + message + '\n')
                # Use merged memory to generate conversation response.
                prompt = generate_prompt("conversation/respond", (memory, working_memory, name, message, ))
                ai_response = call_openai(prompt, 128)
                print("Response: " + ai_response + '\n')

                # Integrate into internal memory.
                prompt = generate_prompt("conversation/integrate", (memory, working_memory, name, message, ai_response,  parameters.features, utils.internalLength(), ))

                await asyncio.get_event_loop().run_in_executor(None, utils.updateInternal, 1, prompt, parameters.internal_capacity)

                working_memory += name + ": " + message.replace('\n', '\n\t') + "\n\n"

                # Decide whether to add to conversation
                pertinent = False
                prompt = generate_prompt("conversation/check_pertinent", (working_memory, ai_response, ))
                resp = call_openai(prompt, 10)
                print(resp)
                if (resp.lower().startswith("yes")):
                    pertinent = True

                if pertinent:
                    working_memory += ": " + ai_response.replace('\n', '\n\t') + "\n\n"
                    await server.sendMessage("MSG:" + ai_response)
                else:
                    working_memory += "|: " + ai_response.replace('\n', '\n\t') + "\n\n"

                # Cut last line of old memory.
                lines = working_memory.split('\n\n')

                if len(lines) > 50:
                    lines = lines[1:]
                    working_memory = '\n\n'.join(lines)
                data.setConversationWorkingMem(working_memory)
            else:
                pass
        except Exception as e:
            print(e)
            connected = False
            server.handleDisconnect(name)
        data.lock.release()
        await asyncio.sleep(0.1)
    await asyncio.sleep(0)
