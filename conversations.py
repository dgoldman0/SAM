from generation import generate_prompt
from generation import call_openai
import asyncio
import data
import utils
import parameters
import system
import random
import time

server = None

# Alter code to have one single group chat.

def init(server_module):
    global server
    server = server_module

# Handle external dialogue. Currently set up so that internal thought processes will only go through one conscious and one subconscious cycle before blocking for the next incoming message.
async def converse(name, socket):
    global server
    connected = True
    last_integrated = time.time()
    steps_since_integration = 0
    # Will still need to lock this loop, just against itself, so that two users interacting at the same time won't cause a mishap with the data. Or just respond back that the system is in the middle of processing another request.
    while connected:
        working_memory = data.getWorkingMemory(2)
            
        internal_memory = data.getMemory(1)
        conversation_memory = data.getMemory(2)
        memory = internal_memory + "\n==================" + conversation_memory + "\n=================="
        try:
            msg = (await socket.recv()).decode()
            # When token limits are increased and cost decreases, it might be useful to give the system access to the previous content window. This would allow it to have a better idea of what the user is talking about, and would allow it to have a better idea of what to say next.
            if msg.startswith("MSG:"):
                now = system.now()
                message = msg[4:]
                print("Received message: " + message + '\n')
                working_memory += name + ": " + message.replace('\n', '\n\t') + "\n\n"

                # Grab external information
                done = False
                capacity = 20000
                iterations = 0
                temp = ""

                while not done and capacity > 0 and iterations < 15:
                    prompt = ""
                    outline = ""
                    if iterations == 0:
                        prompt = generate_prompt("conversation/check_external_initial", (memory, working_memory, temp, now, name, message, capacity, ))
                        outline = call_openai(prompt, 512, 0.75, 'gpt-4')
                        print("Outline: " + outline + "\n")

                    # Does a terrible job of actually using system commands properly.
                    prompt = generate_prompt("conversation/check_external", (now, name, message, outline, temp, capacity, ))
                    command = call_openai(prompt, 256, 0.7, 'gpt-4')
                    print("Command: " + command)
                    result = (await system.processCommand(command)).replace('\n', '\n\t')
                    capacity = capacity - len(result)
                    temp += "||" + result + "\n\n"
                    print("Result: " + result)

                    # Checking if complete
                    prompt = generate_prompt("conversation/check_complete", (outline, temp, ))
                    check_done = call_openai(prompt, 32, 0.7, 'gpt-4')
                    if (check_done.lower().startswith("yes")):
                        done = True

                    iterations += 1
                print("---Done Adding Information---")

                prompt = generate_prompt("conversation/respond", (memory, working_memory + "\n\n" + temp, now, name, message, ))
                ai_response = call_openai(prompt, 512, 0.7, "gpt-4")
                print("Response: " + ai_response + '\n')

                print("Updating Conversation Memory")
                integration_prompt = generate_prompt("conversation/integrate_conversation", (conversation_memory, working_memory + "\n\n" + temp, now, utils.conversationalLength(), ))
                # Will eventually update properly in the updateConversational function.
                conversation_memory = await asyncio.get_event_loop().run_in_executor(None, utils.updateInternal, 2, integration_prompt, parameters.conversation_capacity)
                print("Conversation Memory Updated")
                print("Conversation Memory:\n=====================\n" + conversation_memory + "\n=====================")

                # Generate content view.
                prompt = generate_prompt("conversation/generate_content", (memory, working_memory + "\n\n" + temp, now, name, message, ai_response, ))
                content = call_openai(prompt, 2048, 0.7, "gpt-4")

                if len(temp) > 0:
                    prompt = generate_prompt("conversation/summarize", (temp, ))
                    summary = call_openai(prompt, 2048, 0.7, "gpt-4")
                    print("Summary: " + summary + "\n")
                    working_memory += "\n\n||" + summary + "\n\n"

                working_memory += ": " + ai_response.replace('\n', '\n\t') + "\n\n"
                await server.sendMessage("MSG:" + ai_response)
                await server.sendMessage("CONTENT:" + content)

                steps_since_integration += 1

                # Cut last line of old memory.
                lines = working_memory.split('\n\n')
                # The size of the working memory can be a lot larger since it's using GPT-4 for responses and integration
                if len(lines) > 500:
                    lines = lines[1:]
                    working_memory = '\n\n'.join(lines)
                data.setWorkingMemory(2, working_memory)
            elif msg.startswith("COMMAND:"):
                pass
        except Exception as e:
            print(e)
            connected = False
            server.handleDisconnect(name)
        await asyncio.sleep(0.1)
    await asyncio.sleep(0)