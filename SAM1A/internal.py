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
        ai_response = call_openai(prompt, 128)
        print("Thought: " + ai_response + "\n")
        # Check if there's a command to process.
        if ai_response.lower().startswith("command:"):
            command = ai_response[8:]
            response = await system.process_command(command)
            response = response

            print(response + "\n")
            prompt = generate_prompt("internal/integrate_command", (data.memory_internal, working_memory, command, response, ))
            # Indent new lines to ensure that the system can tell the difference between a multiline message and two lines.
            ai_response = '\t\n'.join(ai_response.split('\n'))
            response = 'system: ' + '\t\n'.join(response.split('\n'))
            working_memory += "<ME>: " + ai_response + "\n\n"
            working_memory += response + "\n\n"
            output = ""
            while not output.endswith("END MEMORY"):
                output = call_openai(prompt, 1800)
            data.memory_internal = output.strip("END MEMORY")
        else:
            prompt = generate_prompt("internal/integrate", (data.memory_internal, working_memory, ai_response, ))
            output = ""
            while not output.endswith("END MEMORY"):
                output = call_openai(prompt, 1800)
            data.memory_internal = output.strip("END MEMORY")
            ai_response = '\t\n'.join(ai_response.split('\n'))
            working_memory += "<ME>: " + ai_response + "\n\n"

        data.save()
        # Cut last line of old memory.
        lines = working_memory.split('\n\n')
        print(str(len(lines)) + '\n')
        if len(lines) > 20:
            lines = lines[1:]
            working_memory = '\n\n'.join(lines)
        thoughts_since_dream += 1
        if thoughts_since_dream == 100:
            thoughts_since_dream = 0
            await dreams.dream()
        else:
            await asyncio.sleep(2.5)
