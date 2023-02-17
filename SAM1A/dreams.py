import data
import asyncio
from generation import generate_prompt
from generation import call_openai
import parameters

async def dream():
    print("Entering dream mode...\n")
    # Keep track of the last thought to give very limited working memory.
    data.set_dreaming(True)
    print ("A")
    data.save()
    print("Starting\n" + data.memory_internal + "\n")
    num_of_dreams = 4
    if data.first:
        num_of_dreams = 1

    for i in range(num_of_dreams):
        print("Dream #" + str(i))
        print("Bootstrapping...")
        prompt = generate_prompt("dreams/bootstrap", (data.memory_internal, ))
        bootstrap = call_openai(prompt, 128, temp = 0.85)
        print("Bootstrap: " + bootstrap + "\n")
        working_memory = bootstrap
        for j in range(10):
            prompt = generate_prompt("dream/step", (data.memory_internal, working_memory, ))
            response = call_openai(prompt, 32, temp = 1)
            prompt = generate_prompt("dream/integrate", (data.memory_internal, working_memory, response, ))
            output = ""
            # Loop while malformed or there's a significant reduction in content length.
            while not output.endswith("END ONTOLOGY") or len(output) < 0.95 * len(data.memory_internal):
                output = call_openai(prompt, parameters.internal_capacity)
            data.memory_internal = output.strip("END ONTOLOGY")
            print(response + "\n")
            working_memory += response + "\n\n"
            await asyncio.sleep(0.1)
    print("Ending\n" + data.memory_internal + "\n")
    data.save()
    data.set_dreaming(False)
