# Internal Layer
from generation import generate_prompt
from generation import call_openai
import asyncio
import data
import dreams
import system
import parameters
import utils
import time

# Notifications don't update internal memory model. It just adds to the working memory, for now anyway.
def notify_connection(name):
    global working_memory
    notice = "system: " + name + " has connected."
    print(notice + "\n")
    working_memory += notice + "\n\n"

def notify_disconnect(name):
    global working_memory
    notice = "system: " + name + " has disconnected."
    print(notice + "\n")
    working_memory += notice + "\n\n"

async def think():
    if data.working_memories[0] == "":
        print("Bootstrapping...")
        prompt = generate_prompt("internal/bootstrap", (data.memory_internal, ))
        bootstrap = call_openai(prompt, 128, temp = 0.85).replace('\n', '\n\t')
        working_memories[0] = bootstrap
    print("Thinking...")
    thoughts_since_dream = 0
    while True:
        if not data.locked:
            data.locked = True
            working_memory = data.working_memories[0]
            prompt = generate_prompt("internal/step_conscious", (data.memory_internal, working_memory, ))
            ai_response = call_openai(prompt, 32, temp = 0.85)
            ai_response = ai_response.replace('\n', '\n\t')
            print("Thought: " + ai_response + "\n")
            # Check if there's a command to process.
            if ai_response.lower().startswith("command:"):
                command = ai_response[8:]
                response = await system.process_command(command)
                response = response.replace('\n', '\n\t')
                prompt = generate_prompt("internal/integrate_command", (data.memory_internal, working_memory, command, response, utils.internalLength, ))
                # Indent new lines to ensure that the system can tell the difference between a multiline message and two lines.
                response = 'system: ' + response
                working_memory += ": " + ai_response + "\n\n"
                working_memory += response + "\n\n"
                await asyncio.get_event_loop().run_in_executor(None, utils.updateInternal, prompt)
            else:
                prompt = generate_prompt("internal/integrate", (data.memory_internal, working_memory, ai_response, utils.internalLength, ))
                output = await asyncio.get_event_loop().run_in_executor(None, utils.updateInternal, prompt)
                working_memory += ": " + ai_response + "\n\n"
            data.working_memories[0] = working_memory
            data.save()
            # Cut last line of old memory.
            lines = working_memory.split('\n\n')
            if len(lines) > 30:
                n = len(lines) - 30
                lines = lines[n:]
                working_memory = '\n\n'.join(lines)
            thoughts_since_dream += 1
            thoughts_to_dream = 50
            if thoughts_since_dream == thoughts_to_dream:
                thoughts_since_dream = 0
                await dreams.dream()
            data.locked = False
            await asyncio.sleep(parameters.thinkpause)
        await asyncio.sleep(0)

# Run simultaneous internal monologues, without access to system resourcs, and which does not receive notifications from external info.
lastsub = 0
async def subthink():
    global lastsub
    # Subcount of zero means no running subconscious.
    if parameters.subs == 0:
        return

    for i in range(parameters.subs):
        print("Bootstrapping subconscious(" + str(i) + ")...")
        prompt = generate_prompt("internal/bootstrap", (data.memory_internal, ))
        bootstrap = call_openai(prompt, 128, temp = 0.85).replace('\n', '\n\t')
        working_memories.append(bootstrap)
    while True:
        if not data.locked:
            data.locked = True
            working_memory = data.working_memories[lastsub + 1]
            prompt = generate_prompt("internal/step_subconscious", (data.memory_internal, working_memory, ))
            ai_response = call_openai(prompt, 32, temp = 0.9)
            ai_response = ai_response.replace('\n', '\n\t')
            print("Subthought(" + str(lastsub) + ")\n")
            prompt = generate_prompt("internal/integrate", (data.memory_internal, working_memory, ai_response, utils.internalLength, ))
            await asyncio.get_event_loop().run_in_executor(None, utils.updateInternal, prompt)
            working_memory += ": " + ai_response + "\n\n"
            data.working_memories[lastsub + 1] = working_memory
            # Cycle through subconsciousness
            lastsub += 1
            if lastsub == parameters.subs:
                lastsub = 0
            data.save()
            data.locked = False
            await asyncio.sleep(parameters.subpause)
        await asyncio.sleep(0)
