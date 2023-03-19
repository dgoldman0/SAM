from generation import generate_prompt
from generation import call_openai
import asyncio
import data
import utils
import parameters
import system
import random

server = None

# Alter code to have one single group chat.

def init(server_module):
    global server
    server = server_module

# Handle external dialogue. Currently set up so that internal thought processes will only go through one conscious and one subconscious cycle before blocking for the next incoming message.
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

                # Check to see if an external command should be called
                prompt = generate_prompt("conversation/check_external", (memory, working_memory, name, message, ))
                command = call_openai(prompt, 128)
                if not command.lower().startswith("none"):
                    print("Command: " + command)
                    result = (await system.processCommand(command)).replace('\n', '\n\t')
                    working_memory += "||" + result + "\n\n"
                    print("Result: " + result)

                # Use merged memory to generate conversation response.
                prompt = generate_prompt("conversation/respond", (memory, working_memory, name, message, ))
                ai_response = call_openai(prompt, 512, 0.7, "gpt-4")
                print("Response: " + ai_response + '\n')

                # Prepare integration statement
                integration_prompt = generate_prompt("conversation/integrate", (memory, working_memory, name, message, ai_response, parameters.features, utils.internalLength(), ))

                working_memory += name + ": " + message.replace('\n', '\n\t') + "\n\n"

                # Decide whether to add to conversation
                pertinent = False
                prompt = generate_prompt("conversation/check_pertinent", (working_memory, ai_response, ))
                resp = call_openai(prompt, 12, 0.7, 'gpt-4')
                print(resp)
                if (resp.lower().startswith("very")):
                    pertinent = True
                elif (resp.lower().startswith("well")):
                    roll = random.randint(0, 19)
                    pertinent = roll > 1
                elif (resp.lower().startswith("somewhat")):
                    roll = random.randint(0, 19)
                    pertinent = roll > 14

                if pertinent:
                    working_memory += ": " + ai_response.replace('\n', '\n\t') + "\n\n"
                    await server.sendMessage("MSG:" + ai_response)
                else:
                    working_memory += "|: " + ai_response.replace('\n', '\n\t') + "\n\n"

                # Execute integration
                await asyncio.get_event_loop().run_in_executor(None, utils.updateInternal, 1, integration_prompt, parameters.internal_capacity)

                # Cut last line of old memory.
                lines = working_memory.split('\n\n')
                # The size of the working memory can be a lot larger since it's using GPT-4 for responses and integration
                if len(lines) > 500:
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
