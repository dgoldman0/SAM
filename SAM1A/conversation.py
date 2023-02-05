from generation import generate_prompt
from generation import call_openai
from generation import generate_image
import io
import asyncio
import data

# External dialogue

working_memory = ""
name = input("Enter your name: ")

async def converse():
    global name, working_memory
    while True:
        message = input(name + ": ")
        if message.startswith('/'):
            if message == "/memory":
                print(data.memory)
            elif message == "/working":
                print(working_memory)
            elif message == "/dream":
                dream()
            elif message == "/save":
                data.save()
        else:
            well_formed = False
            while not well_formed:
                # Merge internal memory into conversation memory.
                prompt = generate_prompt("merge", (data.memory_internal, data.memory, ))
                merged_memory = call_openai(prompt, 2048)
                prompt = generate_prompt("respond", (merged_memory, working_memory, name, message, ))
                ai_response = call_openai(prompt, 128)
                prompt = generate_prompt("integrate", (merged_memory, working_memory, name, message, ai_response, ))
                output = ""
                while not output.endswith("END MEMORY"):
                    output = call_openai(prompt, 1024)
                data.memory = output.strip("END MEMORY")
                prompt = generate_prompt("logic/well_formed", (ai_response, ))
                response = call_openai(prompt, 32)
                if response.lower().startswith("yes"):
                    well_formed = True
            working_memory += name + ": " + message + "\n\n"
            working_memory += "<ME>: " + ai_response + "\n\n"

            # Cut last line of old memory.
            lines = working_memory.split('\n\n')
            if len(lines) > 100:
                lines = lines[1:]
            working_memory = '\n\n'.join(lines)
            print("SAM: " + ai_response)
