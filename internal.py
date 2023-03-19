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
import server
import random

async def think():
    print("Thinking...")
    thoughts_since_dream = 0
    while True:
        if server.connections > 0:
            await data.lock.acquire()
            working_memory = data.getWorkingMemory(1)
            internalmem = data.getMemory(1)
            # Need to fix memory access
            prompt = generate_prompt("internal/step_conscious", (internalmem, working_memory, ))
            ai_response = call_openai(prompt, 32, temp = 0.85)
            ai_response = ai_response.replace('\n', '\n\t')
            print("Thought: " + ai_response + "\n")
            prompt = generate_prompt("internal/integrate", (internalmem, working_memory, ai_response, parameters.features, utils.internalLength(), ))
            output = await asyncio.get_event_loop().run_in_executor(None, utils.updateInternal, 1, prompt, parameters.internal_capacity)
            working_memory += ": " + ai_response + "\n\n"

            # Cut last line of old memory.
            lines = working_memory.split('\n\n')
            if len(lines) > 30:
                n = len(lines) - 30
                lines = lines[n:]
                working_memory = '\n\n'.join(lines)

            data.setWorkingMemory(1, working_memory)

            data.lock.release()
            await asyncio.sleep(parameters.thinkpause)
        await asyncio.sleep(0)

# Run simultaneous internal monologues, without access to system resourcs, and which does not receive notifications from external info.
async def subthink():
    # Subcount of zero means no running subconscious.
    if parameters.subs == 0:
        return

    while True:
        if server.connections > 0:
            await data.lock.acquire()
            # Need to refactor, but now will randomly select the partition
            lastsub = random.randint(0, parameters.subs - 1)
            working_memory = data.getWorkingMemory(lastsub + 2)
            internalmem = data.getMemory(1)
            merged_memory = internalmem
            # Started adding code for subconscious persistent memory
            existingmem = data.getMemory(lastsub + 2)
            if existingmem is not None:
                prompt = generate_prompt("merge", (internalmem, existingmem, ))
                merged_memory = call_openai(prompt, round((parameters.internal_capacity + parameters.conversation_capacity) / 2))
            prompt = generate_prompt("internal/step_subconscious", (merged_memory, working_memory, ))
            ai_response = call_openai(prompt, 32, temp = 0.9)
            ai_response = ai_response.replace('\n', '\n\t')
            print("Subthought(" + str(lastsub) + ")\n")
            if existingmem is not None:
                # Integrate into conversation memory, if it is not blank, otherwise create new base conversation
                prompt = generate_prompt("internal/integrate_sub", (existingmem, working_memory, ai_response, utils.conversationalLength(), ))
                await asyncio.get_event_loop().run_in_executor(None, utils.updateInternal, (lastsub + 2), prompt, parameters.conversation_capacity)
            else:
                print("Bootstrapping subconscious memory (" + str(lastsub) + ")")
                prompt = generate_prompt("internal/bootstrap_sub", (internalmem, ai_response, utils.conversationalLength()))
                mem = call_openai(prompt, parameters.conversation_capacity)
                data.appendMemory(mem)
                data.appendHistory(lastsub + 2, mem)
            # Integrate into internal memory.
            prompt = generate_prompt("internal/integrate_sub_primary", (internalmem, working_memory, ai_response, parameters.features, utils.internalLength(), ))
            await asyncio.get_event_loop().run_in_executor(None, utils.updateInternal, 1, prompt, parameters.internal_capacity)
            # Crashes around here on lastsub == 9
            working_memory += ": " + ai_response + "\n\n"
            # Cut last line of old memory.
            lines = working_memory.split('\n\n')
            if len(lines) > 30:
                n = len(lines) - 30
                lines = lines[n:]
                working_memory = '\n\n'.join(lines)
            data.setWorkingMemory(lastsub + 2, working_memory)

            data.lock.release()
            await asyncio.sleep(parameters.subpause)
        await asyncio.sleep(0)
