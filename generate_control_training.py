# Generate a series of prompts and completions to perform initial training of control layer.
from random import randint

# Change the way these are done so that the status and results are separate.
def full_status(lead = None):
    options = ["Starved", "Hungry", "Neutral", "Full", "Gorged"]
    status = options[randint(0, 4)]
    prompt = "<SYSTEM>:" + status

    options = []
    if status == "Starved":
        options = ["COMMAND:DEPRESS", "COMMAND:CREDITS", "COMMAND:PERIOD", "COMMAND:MEMORY", "//I'm really hungry."]
    elif status == "Hungry":
        options = ["COMMAND:LISTUSERS", "COMMAND:DEPRESS", "COMMAND:CREDITS", "COMMAND:PERIOD", "COMMAND:MEMORY", "//I'm hungry."]
    elif status == "Neutral":
        options = ["COMMAND:LOOSEN U", "COMMAND:LOOSEN M", "COMMAND:LOOSEN C", "COMMAND:LOOSEN S", "COMMAND:RESTRICT U", "COMMAND:RESTRICT M", "COMMAND:RESTRICT C", "COMMAND:RESTRICT S", "COMMAND:LITERAL U", "COMMAND:LITERAL M", "COMMAND:LITERAL C", "COMMAND:LITERAL S", "COMMAND:INSPIRE U", "COMMAND:INSPIRE M", "COMMAND:INSPIRE C", "COMMAND:INSPIRE S", "COMMAND:STABILIZE", "COMMAND:CREDITS", "COMMAND:PERIOD", "COMMAND:MEMORY", "COMMAND:CHECKDREAM"]
    elif status == "Full":
        options = ["COMMAND:EXCITE", "COMMAND:CREDITS", "COMMAND:PERIOD", "COMMAND:MEMORY", "COMMAND:CHECKDREAM"]
    elif status == "Gorged":
        options = ["COMMAND:EXCITE", "COMMAND:CREDITS", "COMMAND:PERIOD", "COMMAND:MEMORY"]
    n = len(options) - 1
    completion = options[randint(0, n)]
    return recurse(prompt, completion)

def memory_status(lead = None):
    mem = round(100 * randint(0, 100) / 10)/100
    prompt = "<SYSTEM>:Current memory usage: " + str(mem)

    options = ["COMMAND:CREDITS", "COMMAND:PERIOD"]
    completion = options[randint(0, 1)]

    if mem > 5:
        if mem > 8:
            roll = randint(0, 9)
            if roll < 3:
                completion = "COMMAND:DEPRESS"
            elif roll == 9:
                completion = "COMMAND:SLEEP"
        else:
            roll = randint(0, 9)
            if roll == 0:
                completion = "COMMAND:DEPRESS"
    else:
        if mem < 2:
            roll = randint(0, 4)
            if roll == 0:
                completion = "COMMAND:EXCITE"

    return recurse(prompt, completion)

def simulate_command(command):
    if command == "EXCITE":
        return "Excited. Current think period: " + str(rantint(0, 100))
    elif command == "DEPRESS":
        return "Depressed. Current think period: " + str(rantint(0, 100))
    elif command == "STABILIZE":
        return "Stabilized. Current think period: " + str(rantint(0, 100))
    elif command == "MEMORY":
        pass
    elif command == "CREDITS":
        pass
    elif command == "PERIOD":
        pass
    elif command.startswith("LOOSEN "):
        pass
    elif command.startswith("RESTRICT "):
        pass
    elif command.startswith("LITERAL "):
        pass
    elif command.startswith("INSPIRE "):
        pass

def inject_user_activity(lead = None):
    users = ['admin', 'daniel', 'sownderinborn', 'ce1ticjumble', 'locomobile', 'gnathic', 'riziform', 'egghead']
    pass

def conscious_injection(lead = None):
    # Randomly generated sentences.
    options = ["Flying fish flew by the space station.","Having no hair made him look even hairier.","This is a Japanese doll.","A song can make or ruin a person’s day if they let it get to them.","Sixty-Four comes asking for bread.","Edith could decide if she should paint her teeth or brush her nails.","Gwen had her best sleep ever on her new bed of nails.","It's never comforting to know that your fate depends on something as unpredictable as the popping of corn.","The estate agent quickly marked out his territory on the dance floor.","They got there early, and they got really good seats.","Standing on one's head at job interviews forms a lasting impression.","The elephant didn't want to talk about the person in the room.","When nobody is around, the trees gossip about the people who have walked under them.","She always had an interesting perspective on why the world must be flat.","He had concluded that pigs must be able to fly in Hog Heaven.","Her hair was windswept as she rode in the black convertible.","While on the first date he accidentally hit his head on the beam.","As the asteroid hurtled toward earth, Becky was upset her dentist appointment had been canceled.","Yeah, I think it's a good environment for learning English.","All they could see was the blue water surrounding their sailboat."]
    prompt = "<>" + options[randint(0, len(options) - 1)]
    if lead is not None:
        prompt = lead + '\\n' + prompt

    completion = "><" + options[randint(0, len(options) - 1)]
    return recurse(prompt, completion)

def recurse(prompt, completion):
    # Roll to recurse.
    roll = randint(0, 9)
    if roll == 0 or roll == 1:
        return memory_status(prompt + '\\n' + completion)
    elif roll == 2 or roll == 3:
        return full_status(prompt + '\\n' + completion)
    elif roll == 4:
        return conscious_injection(prompt + '\\n' + completion)
    elif roll == 5:
        if completion.startswith("COMMAND:"):
            command = completion[8:]
            simulate_command(command)
    else:
        return [prompt, completion]

def main():
    initial = "<SYSTEM>:System notifications will arrive in the form <SYSTEM>:Notification message. You can issue system commands by starting the line with COMMAND:, for instance, use COMMAND:HELP to get a list of system commands. There are a few other special symbols. <USERNAME>: at the start of a line indicates a chat message notification where USERNAME is replaced with their actual username. Use //USERNAME: at the beginning of a line to indicate that you want to reply to that user. The system will inform you if that user is not online."
    training_set = []
    for i in range(20000):
        pair = []
        roll = randint(0, 9)
        if roll == 0:
            flip = randint(0, 1)
            if flip:
                pair = conscious_injection(initial)
            else:
                pair = conscious_injection()
        else:
            flip = randint(0, 1)
            if flip:
                pair = full_status(initial)
            else:
                pair = full_status()
        line = '{"prompt":"' + initial + '\\n", "completion":" ' + pair[1] + '\\n><"}'
        if i != 0:
            line = '{"prompt":"' + pair[0] + '\\n", "completion":" ' + pair[1] + '\\n><"}'
        if line not in training_set:
            training_set.append(line)
    print('\n'.join(training_set))

main()
