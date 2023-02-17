# Internal Layer
from generation import generate_prompt
from generation import call_openai
import asyncio
import data
import dreams
import system
import parameters

working_memory = ""

def check_valid_memory(memory, new_memory):
    if len(new_memory) < 0.95 * len(memory) or not new_memory.endswith("END ONTOLOGY"):
        return false
    return True

def notify_connection(name):
    global working_memory
    notice = "system: " + name + " has connected."
    print(notice + "\n")
    prompt = generate_prompt("internal/integrate", (data.memory_internal, working_memory, notice, ))
    working_memory += notice + "\n\n"
    output = ""
    while output == "":
        output = call_openai(prompt, parameters.internal_capacity)
        if not check_valid_memory(data.memory_internal, output):
            output = ""
    data.memory_internal = output.strip("END ONTOLOGY")

def notify_disconnect(name):
    global working_memory
    notice = "system: " + name + " has disconnected."
    print(notice + "\n")
    prompt = generate_prompt("internal/integrate", (data.memory_internal, working_memory, notice, ))
    working_memory += notice + "\n\n"
    output = ""
    while output == "":
        output = call_openai(prompt, parameters.internal_capacity)
        if not check_valid_memory(data.memory_internal, output):
            output = ""
    data.memory_internal = output.strip("END ONTOLOGY")

async def think():
    global working_memory
    if working_memory == "":
        print("Bootstrapping...")
        prompt = generate_prompt("internal/bootstrap", (data.memory_internal, ))
        bootstrap = call_openai(prompt, 128, temp = 0.85)
        print("Bootstrap: " + bootstrap + "\n")
        working_memory = bootstrap
    print("Thinking")
    thoughts_since_dream = 0
    while True:
        prompt = generate_prompt("internal/step_conscious", (data.memory_internal, working_memory, ))
        ai_response = call_openai(prompt, 32, temp = 0.85)
        print("Thought: " + ai_response + "\n")
        # Check if there's a command to process.
        if ai_response.lower().startswith("command:"):
            command = ai_response[8:]
            response = await system.process_command(command)
            response = response.replace('\n', '\n\t')

            prompt = generate_prompt("internal/integrate_command", (data.memory_internal, working_memory, command, response, ))
            # Indent new lines to ensure that the system can tell the difference between a multiline message and two lines.
            ai_response = ai_response.replace('\n', '\n\t')
            response = 'system: ' + response
            working_memory += ": " + ai_response + "\n\n"
            working_memory += response + "\n\n"
            output = ""
            while output == "":
                output = call_openai(prompt, parameters.internal_capacity)
                if not check_valid_memory(data.memory_internal, output):
                    output = ""
            data.memory_internal = output.strip("END ONTOLOGY")
        else:
            # Going to need to heavily rewrite the integration method to also force the output into the correct format. Or just not have a correct format to maintain.
            prompt = generate_prompt("internal/integrate", (data.memory_internal, working_memory, ai_response, ))
            output = ""
            while output == "":
                output = call_openai(prompt, parameters.internal_capacity)
                if not check_valid_memory(data.memory_internal, output):
                    output = ""
#                print('ratio: ' + str(len(output)/len(data.memory_internal)) + '\n')
#                print(output + "\n\n")
            data.memory_internal = output.strip("END ONTOLOGY")
            ai_response = '\n\t'.join(ai_response.split('\n'))
            working_memory += ": " + ai_response + "\n\n"

        data.save()
        # Cut last line of old memory.
        lines = working_memory.split('\n\n')
        if len(lines) > 30:
            n = len(lines) - 30
            lines = lines[n:]
            working_memory = '\n\n'.join(lines)
        thoughts_since_dream += 1
        thoughts_to_dream = 25
        if thoughts_since_dream == thoughts_to_dream:
            thoughts_since_dream = 0
            await dreams.dream()
        else:
            await asyncio.sleep(0)

# Run simultaneous internal monologues, without access to system resourcs, and which does not receive notifications from external info.
async def subthink():
    working_memories = []
    for i in range(5):
        print("Bootstrapping subconscious(" + str(i) + ")...")
        prompt = generate_prompt("internal/bootstrap", (data.memory_internal, ))
        bootstrap = call_openai(prompt, 128, temp = 0.85)
        print("Bootstrap: " + bootstrap + "\n")
        working_memories.append(bootstrap)
    while True:
        for i in range(5):
            working_memory = working_memories[i]
            prompt = generate_prompt("internal/step_subconscious", (data.memory_internal, working_memory, ))
            ai_response = call_openai(prompt, 32, temp = 0.9)
            print("Subthought(" + str(i) + "): " + ai_response + "\n")
            prompt = generate_prompt("internal/integrate", (data.memory_internal, working_memory, ai_response, ))
            output = ""
            while output == "":
                output = call_openai(prompt, parameters.internal_capacity)
                if not check_valid_memory(data.memory_internal, output):
                    output = ""
            data.memory_internal = output.strip("END ONTOLOGY")
            ai_response = '\n\t'.join(ai_response.split('\n'))
            working_memory += ": " + ai_response + "\n\n"
            working_memories[i] = working_memory
            await asyncio.sleep(0)
        data.save()
