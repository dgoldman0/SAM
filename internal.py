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

# What about doing a merged memory system for both concsious and subconcsious, where their respective persistent memory is updated only, rather than updating both, and that way they can cycle through simultaneously? Maybe do the same for the conscious system. This approach should be good for the core SAM system too.
async def think():
    print("Thinking...")
    thoughts_since_dream = 0
    while True:
        if data.thinking:
            working_memory = data.getWorkingMemory(1)
            internalmem = data.getMemory(1)
            conversationmem = data.getMemory(2)
            memory = internalmem + "\n==================\n" + conversationmem
            partition = random.randint(0, parameters.subs - 1)
            submem = data.getMemory(partition + 3)
            if submem is not None:
                memory += "\n==================\n" + submem + "\n=================="
            # Randomly select a subconscious partition and append it to the internal memory temporarily
            # Need to do a merged memory of all three: conscious, subconscious, and chat
            prompt = generate_prompt("internal/step_conscious", (memory, working_memory, ))
            ai_response = call_openai(prompt, 32, temp = 0.85)
            ai_response = ai_response.replace('\n', '\n\t')
            print("Thought: " + ai_response + "\n")
            now = system.now()
            # Grab external information
            done = False
            capacity = 20000
            iterations = 0
            temp = ""

            # Not finished cleaning up code yet. Will not run. Also, it could be very dangerous to give it unlimited access to commands.
            if parameters.run_commands_internally:
                while not done and capacity > 0 and iterations < 15:
                    prompt = ""
                    outline = ""
                    if iterations == 0:
                        prompt = generate_prompt("conversation/check_external_initial", (memory, working_memory, temp, now, ai_response, capacity, ))
                        outline = call_openai(prompt, 512, 0.75, 'gpt-4')
                        print("Outline: " + outline + "\n")

                    # Does a terrible job of actually using system commands properly.
                    prompt = generate_prompt("conversation/check_external", (now, ai_response, outline, temp, capacity, ))
                    command = call_openai(prompt, 256, 0.7, 'gpt-4')
                    print("Command: " + command)
                    result = (await system.processCommand(command, True)).replace('\n', '\n\t')
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

            await asyncio.sleep(parameters.thinkpause)
        await asyncio.sleep(0)

# Run simultaneous internal monologues, without access to system resourcs, and which does not receive notifications from external info.
async def subthink():
    # Subcount of zero means no running subconscious.
    if parameters.subs == 0:
        return

    while True:
        if server.connections > 0 and data.thinking:
            # Won't need this once each memory is more isolated by the rewrite.
            # Need to refactor, but now will randomly select the partition
            lastsub = random.randint(0, parameters.subs - 1)
            working_memory = data.getWorkingMemory(lastsub + 3)
            internalmem = data.getMemory(1)
            merged_memory = internalmem
            # Instead of "NONE" it should be "", because in the data initialization I should fill these with blanks
            existingmem = data.getMemory(lastsub + 3)
            if existingmem != "":
                prompt = generate_prompt("merge", (internalmem, existingmem, ))
                merged_memory = call_openai(prompt, round((parameters.internal_capacity + parameters.conversation_capacity) / 2))
            prompt = generate_prompt("internal/step_subconscious", (merged_memory, working_memory, ))
            ai_response = call_openai(prompt, 32, temp = 0.9)
            ai_response = ai_response.replace('\n', '\n\t')
            print("Subthought(" + str(lastsub) + ")\n")
            if existingmem != "":
                # Integrate into conversation memory, if it is not blank, otherwise create new base conversation
                prompt = generate_prompt("internal/integrate_sub", (existingmem, working_memory, ai_response, utils.conversationalLength(), ))
                await asyncio.get_event_loop().run_in_executor(None, utils.updateInternal, (lastsub + 3), prompt, parameters.conversation_capacity)
            else:
                print("Bootstrapping subconscious memory (" + str(lastsub) + ")")
                prompt = generate_prompt("internal/bootstrap_sub", (internalmem, ai_response, utils.conversationalLength()))
                mem = call_openai(prompt, parameters.conversation_capacity)
                data.setMemory(lastsub + 3, mem)
                data.appendHistory(lastsub + 3, mem)

            # Crashes around here on lastsub == 9
            working_memory += ": " + ai_response + "\n\n"
            # Cut last line of old memory.
            lines = working_memory.split('\n\n')
            if len(lines) > 30:
                n = len(lines) - 30
                lines = lines[n:]
                working_memory = '\n\n'.join(lines)
            data.setWorkingMemory(lastsub + 3, working_memory)

            await asyncio.sleep(parameters.subpause)
        await asyncio.sleep(0)
