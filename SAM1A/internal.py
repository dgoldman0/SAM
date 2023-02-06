# Internal Layer
from generation import generate_prompt
from generation import call_openai
import asyncio
import data
import dreaming

async def think():
    print("Thinking")
    working_memory = ""
    thoughts_since_dream = 0
    while True:
        prompt = generate_prompt("internal/step", (data.memory_internal, working_memory, ))
        response = call_openai(prompt, 128)
        prompt = generate_prompt("internal/integrate", (data.memory_internal, working_memory, response, ))
        output = ""
        while not output.endswith("END MEMORY"):
            output = call_openai(prompt, 1800)
        data.memory_internal = output.strip("END MEMORY")
        data.save()
        print("Thought: " + response + "\n")
        working_memory += response + "\n\n"

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
