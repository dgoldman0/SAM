def check_valid_memory(memory, new_memory):
    try:
        if len(new_memory) < 0.90 * len(memory):
            print("Fails Basic: " + str(len(new_memory)/len(memory) * 100) + "\n\n")
            return False
            if not new_memory.endswith("END MEMORY"):
                print("Fails Basic: " + new_memory + "\n\n")
                return False
        return True
        # Force a formal ontology structure. Doing so may not be the best option. Testing should be done to see.
        op_loc = new_memory.find("Object Properties:\n")
        a_loc = new_memory.find("Axioms:\n")
        if op_loc == -1 or a_loc == -1:
            print(new_memory + "\n")
            print("Parts Missing\n")
            return False
        classes = new_memory[9:op_loc].strip()
        ops = new_memory[op_loc + 19:a_loc].strip()
        axioms = new_memory[a_loc + 8:].strip("END MEMORY").strip()
        lines = classes.split("\n") + ops.split('\n') + axioms.split('\n')
        i = 0
        while i < len(lines):
            line = lines[i].strip()
            if not line == "" and not line.startswith('-'):
                print(line)
                print("Malformed\n")
                return False
            i += 1
        return True
    except Exception as e:
        print(e)
