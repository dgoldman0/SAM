# Internal Layer
from generation import generate_prompt
from generation import call_openai
import asyncio
import data
import dreams
import system
import parameters

working_memory = ""

def notify_connection(name):
    global working_memory
    notice = "system: " + name + " has connected."
    print(notice + "\n")
    prompt = generate_prompt("internal/integrate", (data.memory_internal, working_memory, notice, ))
    working_memory += notice + "\n\n"
    output = ""
    while not output.endswith("END MEMORY"):
        output = call_openai(prompt, parameters.internal_capacity)
    data.memory_internal = output.strip("END MEMORY")

def notify_disconnect(name):
    global working_memory
    notice = "system: " + name + " has disconnected."
    print(notice + "\n")
    prompt = generate_prompt("internal/integrate", (data.memory_internal, working_memory, notice, ))
    working_memory += notice + "\n\n"
    output = ""
    while not output.endswith("END MEMORY"):
        output = call_openai(prompt, parameters.internal_capacity)
    data.memory_internal = output.strip("END MEMORY")

async def think():
    global working_memory
    if working_memory == "":
        print("Bootstrapping...")
        prompt = generate_prompt("internal/bootstrap", (data.memory_internal, ))
        bootstrap = call_openai(prompt, 128, temp = 0.85)
        print("Bootstrap: " + bootstrap + "\n")
        working_memory = bootstrap
    print("Thinking")
    thoughts_since_dream = 0
    while True:
        prompt = generate_prompt("internal/step_conscious", (data.memory_internal, working_memory, ))
        ai_response = call_openai(prompt, 32, temp = 0.85)
        print("Thought: " + ai_response + "\n")
        # Check if there's a command to process.
        if ai_response.lower().startswith("command:"):
            command = ai_response[8:]
            response = await system.process_command(command)
            response = response.replace('\n', '\n\t')

            prompt = generate_prompt("internal/integrate_command", (data.memory_internal, working_memory, command, response, ))
            # Indent new lines to ensure that the system can tell the difference between a multiline message and two lines.
            ai_response = ai_response.replace('\n', '\n\t')
            response = 'system: ' + response
            working_memory += ": " + ai_response + "\n\n"
            working_memory += response + "\n\n"
            output = ""
            # Loop while malformed or there's a significant reduction in content length.
            while not output.endswith("END MEMORY") or len(output) < 0.95 * len(data.memory_internal):
                output = call_openai(prompt, parameters.internal_capacity)
            data.memory_internal = output.strip("END MEMORY")
        else:
            prompt = generate_prompt("internal/integrate", (data.memory_internal, working_memory, ai_response, ))
            output = ""
            # Loop while malformed or there's a significant reduction in content length.
            while not output.endswith("END MEMORY") or len(output) < 0.95 * len(data.memory_internal):
                output = call_openai(prompt, parameters.internal_capacity)
                print('ratio: ' + str(len(output)/len(data.memory_internal)) + '\n')
            data.memory_internal = output.strip("END MEMORY")
            ai_response = '\n\t'.join(ai_response.split('\n'))
            working_memory += ": " + ai_response + "\n\n"

        data.save()
        # Cut last line of old memory.
        lines = working_memory.split('\n\n')
        if len(lines) > 30:
            n = len(lines) - 30
            lines = lines[n:]
            working_memory = '\n\n'.join(lines)
        thoughts_since_dream += 1
        thoughts_to_dream = 25
        if thoughts_since_dream == thoughts_to_dream:
            thoughts_since_dream = 0
            await dreams.dream()
        else:
            await asyncio.sleep(0)

# Run simultaneous internal monologues, without access to system resourcs, and which does not receive notifications from external info.
async def subthink():
    working_memories = []
    for i in range(5):
        print("Bootstrapping subconscious(" + str(i) + ")...")
        prompt = generate_prompt("internal/bootstrap", (data.memory_internal, ))
        bootstrap = call_openai(prompt, 128, temp = 0.85)
        print("Bootstrap: " + bootstrap + "\n")
        working_memories.append(bootstrap)
    while True:
        for i in range(5):
            working_memory = working_memories[i]
            print(working_memory)
            prompt = generate_prompt("internal/step_subconscious", (data.memory_internal, working_memory, ))
            ai_response = call_openai(prompt, 32, temp = 0.9)
            print("Subthought(" + str(i) + "): " + ai_response + "\n")
            prompt = generate_prompt("internal/integrate", (data.memory_internal, working_memory, ai_response, ))
            output = ""
            # Loop while malformed or there's a significant reduction in content length.
            while not output.endswith("END MEMORY") or len(output) < 0.95 * len(data.memory_internal):
                output = call_openai(prompt, parameters.internal_capacity)
                print('ratio: ' + str(len(output)/len(data.memory_internal)) + '\n')
            data.memory_internal = output.strip("END MEMORY")
            ai_response = '\n\t'.join(ai_response.split('\n'))
            working_memory += ": " + ai_response + "\n\n"
            working_memories[i] = working_memory
            await asyncio.sleep(0)
        data.save()
