import io

memory = "<ME>"
memory_internal = "<ME>"

try:
    file = open('memory.txt',mode='r')
    memory = file.read()
    file.close()
    file = open('memory_internal.txt',mode='r')
    memory = file.read()
    file.close()
except Exception as e:
    pass

def save():
    try:
        file = open('memory.txt',mode='w')
        file.write(memory)
        file.close()
        file = open('memory_internal.txt',mode='w')
        file.write(memory_internal)
        file.close()
    except Exception as e:
        pass
