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
            print("Fails Suffix Requirement\n\n")
            return False
        return True
    except Exception as e:
        print(e)

def updateInternal(mem_id, prompt, capacity):
    print("Updating...\n")
    print(prompt)
    output = ""
    internalmem = data.getMemory(mem_id)
    while output == "":
        temp = 0.9
        model = "gpt-3.5-turbo"
        if mem_id < 3:
            temp = 0.7
            model = "gpt-4"
        output = call_openai(prompt, capacity, temp, model).strip().strip('.')
        if not checkValidMemory(internalmem, output):
            output = ""
    cleaned = output.removesuffix("END MEMORY")
    data.setMemory(mem_id, cleaned)
    data.appendHistory(mem_id, cleaned)
    print("Finished...\n")
    return output

# Get the approximate length of memory capacity in words
def internalLength():
    return round(parameters.internal_capacity * 4 / 7.5)

def conversationalLength():
    return round(parameters.conversation_capacity * 4 / 7.5)
