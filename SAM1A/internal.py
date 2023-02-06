# Internal Layer
from generation import generate_prompt
from generation import call_openai
import asyncio
import data
import dreams
import system

working_memory = ""

def notify_connection(name):
    global working_memory
    notice = "system: " + name + " has connected."
    print(notice + "\n")
    prompt = generate_prompt("internal/integrate", (data.memory_internal, working_memory, notice, ))
    working_memory += notice + "\n\n"
    output = ""
    while not output.endswith("END MEMORY"):
        output = call_openai(prompt, 1800)
    data.memory_internal = output.strip("END MEMORY")

def notify_disconnect(name):
    global working_memory
    notice = "system: " + name + " has disconnected."
    print(notice + "\n")
    prompt = generate_prompt("internal/integrate", (data.memory_internal, working_memory, notice, ))
    working_memory += notice + "\n\n"
    output = ""
    while not output.endswith("END MEMORY"):
        output = call_openai(prompt, 1800)
    data.memory_internal = output.strip("END MEMORY")

async def think():
    global working_memory
    print("Thinking")
    thoughts_since_dream = 0
    while True:
        prompt = generate_prompt("internal/step", (data.memory_internal, working_memory, ))
        response = call_openai(prompt, 128)
        print("Thought: " + response + "\n")
        # Check if there's a command to process.
        if response.lower().startswith("command:"):
            command = response[8:].lower()
            response = await system.process_command(command)
            response = "system: " + response
            print(response + "\n")
            prompt = generate_prompt("internal/integrate_command", (data.memory_internal, working_memory, command, response, ))
            working_memory += response + "\n\n"
            output = ""
            while not output.endswith("END MEMORY"):
                output = call_openai(prompt, 1800)
            data.memory_internal = output.strip("END MEMORY")
        else:
            prompt = generate_prompt("internal/integrate", (data.memory_internal, working_memory, response, ))
            output = ""
            while not output.endswith("END MEMORY"):
                output = call_openai(prompt, 1800)
            data.memory_internal = output.strip("END MEMORY")
            working_memory += "<ME>: " + response + "\n\n"

        data.save()
        # Cut last line of old memory.
        lines = working_memory.split('\n\n')
        if len(lines) > 20:
            lines = lines[1:]
        working_memory = '\n\n'.join(lines)
        thoughts_since_dream += 1
        if thoughts_since_dream == 100:
            thoughts_since_dream = 0
            await dreams.dream()
        else:
            await asyncio.sleep(2.5)
