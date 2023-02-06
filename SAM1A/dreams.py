import data
import asyncio

async def dream():
    print("Entering dream mode...\n")
    working_memory = ""
    # Keep track of the last thought to give very limited working memory.
    data.set_dreaming()
    data.save()
    print("Starting\n" + data.memory_internal + "\n")
    for i in range(4):
        print("Dream #" + str(i))
        for j in range(3):
            prompt = generate_prompt("dream/step", (data.memory_internal, working_memory, ))
            response = call_openai(prompt, 128)
            prompt = generate_prompt("dream/integrate", (data.memory_internal, working_memory, response, ))
            output = ""
            while not output.endswith("END MEMORY"):
                output = call_openai(prompt, 1800)
            data.memory_internal = output.strip("END MEMORY")
            print(response + "\n")
            working_memory += response + "\n\n"
            asyncio.sleep(0)
        working_memory = ""
    print("Ending\n" + data.memory_internal + "\n")
    data.save()
    data.set_awake()
