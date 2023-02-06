# Internal Layer
from generation import generate_prompt
from generation import call_openai
import asyncio
import data
import dreams
import system

async def think():
    print("Thinking")
    working_memory = ""
    thoughts_since_dream = 0
    while True:
        # I can't figure out if this paradigm is better or if I should have a separate integrate prompt for when there's a command request.
        prompt = generate_prompt("internal/step", (data.memory_internal, working_memory, ))
        response = call_openai(prompt, 128)
        prompt = generate_prompt("internal/integrate", (data.memory_internal, working_memory, response, ))
        output = ""
        while not output.endswith("END MEMORY"):
            output = call_openai(prompt, 1800)
        data.memory_internal = output.strip("END MEMORY")
        print("Thought: " + response + "\n")
        working_memory += "<ME>: " + response + "\n\n"

        # Check if there's a command to process.
        if response.lower().startswith("command:"):
            command = response[8:].lower()
            response = "system: " + system.process_command(command)
            print(response + "\n")
            prompt = generate_prompt("internal/integrate", (data.memory_internal, working_memory, response, ))
            working_memory += response + "\n\n"
            output = ""
            while not output.endswith("END MEMORY"):
                output = call_openai(prompt, 1800)
            data.memory_internal = output.strip("END MEMORY")

        data.save()
        # Cut last line of old memory.
        lines = working_memory.split('\n\n')
        if len(lines) > 20:
            lines = lines[1:]
        working_memory = '\n\n'.join(lines)
        thoughts_since_dream += 1
        if thoughts_since_dream == 20:
            thoughts_since_dream = 0
            await dreams.dream()
        else:
            await asyncio.sleep(5)
