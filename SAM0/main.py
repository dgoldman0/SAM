from generation import generate_prompt
from generation import call_openai
from generation import generate_image
import io

memory = "<ME>"
working_memory = ""
name = input("Enter your name: ")

try:
    file = open('memory.txt',mode='r')
    memory = file.read()
    file.close()
except Exception as e:
    pass

def dream():
    global memory, working_memory
    # Keep track of the last thought to give very limited working memory.
    print("Starting\n" + memory + "\n")
    for i in range(4):
        print("Dream #" + str(i))
        for j in range(3):
            prompt = generate_prompt("dream/step", (memory, working_memory, ))
            response = call_openai(prompt, 128)
            prompt = generate_prompt("dream/integrate", (memory, working_memory, response, ))
            output = ""
            while not output.endswith("END ONTOLOGY"):
                output = call_openai(prompt, 2048)
            memory = output.strip("END ONTOLOGY")
            print(response + "\n")
            working_memory += response + "\n\n"
        working_memory = ""
    print("Ending\n" + memory + "\n")

def converse():
    global memory, working_memory, name
    while True:
        message = input(name + ": ")
        if message.startswith('/'):
            if message == "/memory":
                print(memory)
            elif message == "/working":
                print(working_memory)
            elif message == "/dream":
                dream()
            elif message == "/save":
                try:
                    file = open('memory.txt',mode='w')
                    file.write(memory)
                    file.close()
                except Exception as e:
                    pass
        else:
            well_formed = False
            while not well_formed:
                prompt = generate_prompt("respond", (memory, working_memory, name, message, ))
                ai_response = call_openai(prompt, 128)
                prompt = generate_prompt("integrate", (memory, working_memory, name, message, ai_response, ))
                output = ""
                while not output.endswith("END ONTOLOGY"):
                    output = call_openai(prompt, 2048)
                memory = output.strip("END ONTOLOGY")
                prompt = generate_prompt("logic/well_formed", (ai_response, ))
                response = call_openai(prompt, 32)
                if response.lower().startswith("yes"):
                    well_formed = True
            working_memory += name + ": " + message + "\n\n"
            working_memory += "<ME>: " + ai_response + "\n\n"
            print("SAM: " + ai_response)

converse()
