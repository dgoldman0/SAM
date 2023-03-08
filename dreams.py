import data
import asyncio
from generation import generate_prompt
from generation import call_openai
import parameters
import utils

# Will need major updating. Also considering using subconscious too.

async def dream():
    return # Doesn't work right now.
    print("Entering dream mode...\n")
    # Keep track of the last thought to give very limited working memory.
    data.set_dreaming(True)
    print ("A")
    
    print("Starting\n" + data.memory_internal + "\n")
    num_of_dreams = 5
    if data.first:
        num_of_dreams = 1

    pairs = [];
    for i in range(num_of_dreams):
        print("Dream #" + str(i))
        print("Bootstrapping...")
        prompt = generate_prompt("dreams/bootstrap", (data.memory_internal, ))
        bootstrap = call_openai(prompt, 128, temp = 0.85)
        print("Bootstrap: " + bootstrap + "\n")
        working_memory = bootstrap
        for j in range(50):
            prompt = generate_prompt("dream/step", (data.memory_internal, working_memory, ))
            response = call_openai(prompt, 32, temp = 1)
            # Add each dream step to the list of training pairs
            pairs.append((prompt, response, ));
            prompt = generate_prompt("dream/integrate", (data.memory_internal, working_memory, response, ))
            # Not sure if this works right, because I thought it gets a future instead
            output = await asyncio.get_event_loop().run_in_executor(None, utils.updateInternal, prompt)
            # Add memory changes to the training data
            pairs.append((prompt, output, ));
            print(response + "\n")
            working_memory += response + "\n\n"
            await asyncio.sleep(0.1)
    print("Ending\n" + data.memory_internal + "\n")
    # Train based off of these pairs.
    data.train(pairs);
    
    data.set_dreaming(False)
