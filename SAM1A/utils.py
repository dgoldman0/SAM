def check_valid_memory(memory, new_memory):
    if len(new_memory) < 0.95 * len(memory) or not new_memory.startswith("Classes:\n") or not new_memory.endswith("END ONTOLOGY"):
        return False

    # Force a formal ontology structure. Doing so may not be the best option. Testing should be done to see.
    op_loc = new_memory.find("Object Properties:\n")
    a_loc = new_memory.find("Axioms:\n")
    if op_loc == -1 or a_loc == -1:
        return False
    ops = new_memory[op_loc + 19:a_loc].strip()
    axioms = new_memory[a_loc + 8:].strip("END ONTOLOGY").strip()
    lines = ops.split('\n').append(axioms.split('\n'))
    i = 0
    while i < len(lines):
        if not lines[i].startswith('-'):
            return False
        i += 1
    return True
