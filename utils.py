from generation import generate_prompt
from generation import call_openai
import data
import parameters

def checkValidMemory(memory, new_memory):
    try:
        if len(new_memory) < parameters.contraction_tolerance * len(memory):
            print("Fails Basic: " + str(len(new_memory)/len(memory) * 100) + "\n\n")
            return False
        if not new_memory.endswith("END MEMORY"):
            print("Fails Basic: " + new_memory + "\n\n")
            return False
        return True
    except Exception as e:
        print(e)

def updateInternal(mem_id, prompt, capacity):
    print("Updating...\n")
    output = ""
    internalmem = data.getMemory(mem_id)
    while output == "":
        output = call_openai(prompt, capacity).strip().strip('.')
        if not checkValidMemory(internalmem, output):
            output = ""
    data.setMemory(mem_id, output.strip("END MEMORY"))
    print("Finished...\n")
    return output

# Not updated to database format yet
def updateConversational(prompt):
    print("Updating...\n")
    output = ""
    while output == "":
        output = call_openai(prompt, parameters.conversation_capacity)
        if not checkValidMemory(data.memory, output):
            output = ""
    data.memory = output.strip("END MEMORY")
    print("Finished...\n")
    return output

# Get the approximate length of memory capacity in words
def internalLength():
    return round(parameters.internal_capacity * 4 / 3.5)

def conversationalLength():
    return round(parameters.conversation_capacity * 4 / 3.5)
