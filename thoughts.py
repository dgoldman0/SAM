import globals
import physiology

sub_history = globals.sub_history

# Good to test code with the super cheap basic models, at least to check for errors. In the final version, the conscious and subconscious models might be different from each other to allow the inner workings of SAM's mind to be different from the conscious workings. The most recent trained model names will also have to be obtained.

conscious = "davinci"
subconscious = "davinci"

# The current user that SAM is listening to, if any.
active_user = ""

# The number of subconscious partitions. Currently fixed, but will be variable.
total_partitions = 3

# Generate a subconscious thought and propogate to a conscious thought
def step_subconscious(partition):
    global sub_history

    # Get next completion from the subconscious based on existing subconscious dialogue.
    next_prompt = openai.Completion.create(
        model=subconscious,
        temperature=1,
        max_tokens=75,
        top_p=0.5,
        frequency_penalty=0.5,
        presence_penalty=0.5,
        prompt=sub_history[partition] + "\n",
        stop="\n")["choices"][0]["text"].strip()
    sub_history[partition] = sub_history[partition] + "\nSubconscious: " + next_prompt

    # Get next completion for the conscious dialog, using subconscious history as the prompt (subconscious injecting itself into consciousness)
    next_prompt = openai.Completion.create(
        model=conscious,
        temperature=0.9,
        max_tokens=125,
        top_p=0.5,
        frequency_penalty=1,
        presence_penalty=1,
        prompt=sub_history[partition] + "\n",
        stop="\n")["choices"][0]["text"].strip()
    globals.history = globals.history + "\nConscious: " + next_prompt
    sub_history[partition] = sub_history[partition] + "\nConscious: " + next_prompt

# One iteration of inner dialog. This method needs to be able to initiate communications with users so it needs websockets. Or it could use a log.
def step_conscious(websocket):
    global history
    global sub_history
    next_prompt = openai.Completion.create(
        model=conscious,
        temperature=physiology.temp,
        max_tokens=125,
        top_p=physiology.top_p,
        frequency_penalty=0.5,
        presence_penalty=0.5,
        prompt=globals.history + "\n",
        stop="\n")["choices"][0]["text"].strip()

    # Replace with the system command to speak to a given user.
    #if (next_prompt.startswith("Sam:")):
    #    next_prompt = next_prompt.replace("Sam:", "").replace("User:", "").replace("Conscious:", "").replace("Subconscious:", "").strip()
    #    globals.history = globals.history + "\nSam: " + next_prompt
    else:
        globals.history = globals.history + "\nConscious: " + next_prompt
        partitions = len(sub_history)
        if partitions > 1:
            # Flip to see if the conscious thought should be added to the subconscious log.
            flip = random.randint(0, 1)
            if flip:
                partition = random.randint(0, partitions - 1)
                sub_history[partition] = sub_history[partition] + "\nConscious: " + next_prompt

# Generate response to user input. In the future, the system will be able to ignore user input if it "wants" to. Basically, it will be able to choose to pay attention or not. "Sam" as the preface is basically indicating that it was spoke outloud.
def respond_to_user(username, user_input):
    global sub_history
    global active_user

    if active_user == username:
        globals.history = globals.history + "\n" + username + ": " + user_input.strip()
        next_prompt = openai.Completion.create(
            model=conscious,
            temperature=0.4,
            max_tokens=250,
            top_p=0.5,
            frequency_penalty=1,
            presence_penalty=1,
            prompt=globals.history + "\n",
            # The system tends to spit out a lot copies of the tags, but maybe that should be normal and maybe I shouldn't cut them out.
            stop="\n")["choices"][0]["text"].strip()

        globals.history = globals.history + "\nSam: " + next_prompt
    else:
        # The user input is "background noise." Have it processed by random partition of the subconscious.
        partition = random.randint(0, total_partitions)
        next_prompt = openai.Completion.create(
            model=subconscious,
            temperature=1,
            max_tokens=75,
            top_p=0.5,
            frequency_penalty=0.5,
            presence_penalty=0.5,
            prompt=sub_history[partition] + "\n",
            stop="\n")["choices"][0]["text"].strip()
        sub_history[partition] = sub_history[partition] + "\nSubconscious: " + next_prompt
    return next_prompt

# Inner dialog loop
def think(lock, websocket):
    global history
    while True:
        lock.acquire()
        step_conscious(lock)

        # Cut off old information when past the capacity.
        if (len(globals.history) > physiology.history_capacity):
            loc = globals.history.index("\n")
            if (loc is not None):
                globals.history = globals.history[loc + 1:]
        lock.release()
        time.sleep(physiology.think_period)

# Subconscious to conscious interaction loops
def sub_think(partition, lock):
    global sub_history
    while True:
        lock.acquire()
        step_subconscious(partition, lock)

        # Cut off old information when past the capacity.
        if (len(sub_history[partition]) > physiology.subhistory_capacity):
            loc = sub_history[partition].index("\n")
            if (loc is not None):
                sub_history[partition] = sub_history[partition][loc + 1:]
        lock.release()
        time.sleep(6)

# Awaken AI either upon bootup or after sleeping.
def wake_ai():
    # System notification to AI of wakeup. Should include various status information once I figure out what to include.
    print("AI Waking Up")
    startup_message = "System Notifications: Waking up."
    globals.history += startup_message

    # Begin inner dialog
    t = Thread(target=think, args=[lock], daemon=True)
    print("Starting Inner Dialog")
    t.start()

    # Start three partitions of subconscious dialog after the user replies, one at a time. It would be better if the number of partitions is variable. A large number would indicate deep contemplation, and would be more resource intensive. The fatique feature would have to limit the number of partitions, which would also interestingly enough result in things like brain fog. Though the hope is to generally have enough resources to avoid this issue.
    for partition in range(3):
        # Wait three seconds to start each partition to give time for inner dialog to propogate.
        time.sleep(3)
        t = Thread(target=sub_think, args=[partition, lock], daemon=True)
        print("Starting Subconscious Partition #" + partition)
        t.start()
