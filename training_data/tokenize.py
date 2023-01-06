import sys
import io
from random import randint

# Create prompts and completions by randomly breaking up the history into chunks between 1 and 5 lines long, multiple times. Right now 3, but will change based on a number of factors.
def split(text, iterations = 5, min = 1, max = 10):
    training = []
    for i in range(iterations):
        cur = 0
        while cur < len(text) - 2:
            prompt = []
            completion = []
            prompt_size = randint(min,max)
            completion_size = randint(min, max)
            if len(text) > cur + prompt_size + completion_size:
                prompt = text[cur:cur + prompt_size]
                completion = text[cur + prompt_size:cur + prompt_size + completion_size]
                cur += (prompt_size + completion_size)
            else:
                prompt = text[cur:-1]
                completion = text[-1]
                cur = len(text)
            if len(completion) > 0:
                line = '{"prompt":"' + (".".join(prompt)).replace('\\', '\\\\').replace('"', '\\"') + '\\n", "completion":" ' + ('.'.join(completion)).replace('\\', '\\\\').replace('"', '\\"') + '\\n><"}'
                if line not in training:
                    training.append(line)
    return training

if len(sys.argv) == 3:
    input_filename = sys.argv[1]
    output_filename = sys.argv[2]
    input_file = open(input_filename, "r")
    input = input_file.read().replace('\n', '\\n')
    input_file.close()
    training = split(input.split('.'), 100)
    output_file = open(output_filename, "w")
    output_file.write('\n'.join(training))
    output_file.close()
else:
    print("Invalid number of arguments. Please include input file name and output file name.")
