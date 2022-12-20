import globals

# Generate a subconscious thought and propogate to a conscious thought
def step_subconscious(partition):
    global history
    global sub_history

    # Get next completion from the subconscious based on existing subconscious dialogue.
    next_prompt = openai.Completion.create(
        model=subconscious,
        temperature=1,
        max_tokens=75,
        top_p=0.5,
        frequency_penalty=0.5f,
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
    history = history + "\nConscious: " + next_prompt
    sub_history[partition] = sub_history[partition] + "\nConscious: " + next_prompt

# One iteration of inner dialog. This method needs to be able to initiate communications with users so it needs websockets. Or it could use a log.
def step_conscious(websocket):
    global history
    global sub_history
    next_prompt = openai.Completion.create(
        model=conscious,
        temperature=0.5,
        max_tokens=125,
        top_p=0.7,
        frequency_penalty=1,
        presence_penalty=1,
        prompt=history + "\n",
        stop="\n")["choices"][0]["text"].strip()

    # If the prompt starts with Sam,
    if (next_prompt.startswith("Sam:")):
        next_prompt = next_prompt.replace("Sam:", "").replace("User:", "").replace("Conscious:", "").replace("Subconscious:", "").strip()
        history = history + "\nSam: " + next_prompt
        full_history = full_history + "\n<Sam>: " + next_prompt
    else:
        history = history + "\nConscious: " + next_prompt
        partitions = len(sub_history)
        if partitions > 1:
            # Flip to see if the conscious thought should be added to the subconscious log.
            flip = random.randint(0, 1)
            if flip:
                partition = random.randint(0, partitions - 1)
                sub_history[partition] = sub_history[partition] + "\nConscious: " + next_prompt

# This method is not set up for multiple users. That's a problem. In fact, it is not set up for websocket either.
def respond_to_user(user_input, websocket):
    global history
    global sub_history
    # User: will have to be replaced with something else. Perhaps an indication that a given user is the active focus.
    history = history + "\nUser: " + user_input.strip()
    full_history = full_history + "\n<User>: " + user_input.strip()
    next_prompt = openai.Completion.create(
        model=conscious,
        temperature=0.4,
        max_tokens=250,
        top_p=1,
        frequency_penalty=1,
        presence_penalty=1,
        prompt=history + "\n",
        stop="\n")["choices"][0]["text"].replace("Sam:", "").replace("User:", "").replace("Conscious:", "").replace("Subconscious:", "").strip()

    history = history + "\nSam: " + next_prompt

    return next_prompt

# Inner dialog loop
def think(lock, websocket):
    global history
    while True:
        lock.acquire()
        step_conscious(lock)
        # Prevent the prompt from getting too long by cutting off old chat history
        if (len(history) > 5120):
            loc = history.index("\n")
            if (loc is not None):
                history = history[loc + 1:]
        lock.release()
        time.sleep(2)

# Subconscious to conscious interaction loops
def sub_think(partition, lock):
    global sub_history
    while True:
        lock.acquire()
        step_subconscious(partition, lock)
        # Prevent the prompt from getting too long by cutting off old chat history. Subconscious history is much shorter to keep it dynamic and save on computation.
        if (len(sub_history[partition]) > 500):
            loc = sub_history[partition].index("\n")
            if (loc is not None):
                sub_history[partition] = sub_history[partition][loc + 1:]
        lock.release()
        time.sleep(6)

# Bootup AI
def wake_ai():
    global history
    global lock

    # System notification to AI of wakeup. Should include various status information once I figure out what to include.
    print("AI Starting Up")
    startup_message = "System Notifications: Waking up."

    # Begin inner dialog
    t = Thread(target=think, args=[lock], daemon=True)
    print("Starting Inner Dialog")
    t.start()

    # Start three partitions of subconscious dialog after the user replies, one at a time. It would be better if the number of partitions is variable. A large number would indicate deep contemplation, and would be more resource intensive. The fatique feature would have to limit the number of partitions, which would also interestingly enough result in things like brain fog. Though the hope is to generally have enough resources to avoid this issue.
    for partition in range(3):
        # Wait three seconds to start each partition to give time for inner dialog to propogate.
        time.sleep(3)
        t = Thread(target=sub_think, args=[partition, lock], daemon=True)
        print("Starting Subconscious Partition " + partition)
        t.start()
