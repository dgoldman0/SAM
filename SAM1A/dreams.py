import data

def dream(start):
    working_memory = start
    # Keep track of the last thought to give very limited working memory.
    print("Starting\n" + data.memory_internal + "\n")
    for i in range(4):
        print("Dream #" + str(i))
        for j in range(3):
            prompt = generate_prompt("dream/step", (data.memory_internal, working_memory, ))
            response = call_openai(prompt, 128)
            prompt = generate_prompt("dream/integrate", (data.memory_internal, working_memory, response, ))
            output = ""
            while not output.endswith("END MEMORY"):
                output = call_openai(prompt, 1024)
            data.memory_internal = output.strip("END MEMORY")
            print(response + "\n")
            working_memory += response + "\n\n"
        working_memory = ""
    print("Ending\n" + data.memory_internal + "\n")
