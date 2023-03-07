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

def updateInternal(prompt):
    print("Updating...\n")
    output = ""
    while output == "":
        output = call_openai(prompt, parameters.internal_capacity).strip().strip('.')
        if not checkValidMemory(data.memory_internal, output):
            output = ""
    data.memory_internal = output.strip("END MEMORY")
    print("Finished...\n")
    return output

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
