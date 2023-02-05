# Internal Layer
import asyncio
import data

async def think():
    while True:
        prompt = generate_prompt("internal/step", (data.memory_internal, working_memory, ))
        response = call_openai(prompt, 128)
        prompt = generate_prompt("internal/integrate", (data.memory_internal, working_memory, response, ))
        output = ""
        while not output.endswith("END MEMORY"):
            output = call_openai(prompt, 1024)
        data.memory_internal = output.strip("END MEMORY")
        print(response + "\n")
        working_memory += response + "\n\n"

        # Cut last line of old memory.
        lines = working_memory.split('\n\n')
        if len(lines) > 100:
            lines = lines[1:]
        working_memory = '\n\n'.join(lines)
