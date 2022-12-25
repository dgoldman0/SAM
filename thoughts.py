import openai
import time
import random
from threading import Thread
from threading import Event
import time

import globals
import physiology
import monitoring
import system

# Maybe replace threading with aioschedule if possible.

sub_history = globals.sub_history

# Good to test code with the super cheap basic models, at least to check for errors. In the final version, the conscious and subconscious models might be different from each other to allow the inner workings of SAM's mind to be different from the conscious workings. The most recent trained model names will also have to be obtained.

conscious = "text-davinci-003"
subconscious = "text-davinci-003"

# The current user that SAM is listening to, if any, and set the time at which it was changed.
active_user = ""
active_last_changed = 0

total_partitions = 0

partition_controls = []

async def set_active_user(username):
    active_user = username
    active_last_changed = time.time()

# Generate a subconscious thought.
def step_subconscious(partition):
    global sub_history

    # Get next completion from the subconscious based on existing subconscious dialogue. Maybe add randomness by seeding with random thoughts.
    try:
        next_prompt = openai.Completion.create(
            model=subconscious,
            temperature=physiology.subconscious_temp,
            max_tokens=75,
            top_p=physiology.subconscious_top_p,
            frequency_penalty=0.5,
            presence_penalty=0.5,
            prompt=sub_history[partition],
            stop="\n")["choices"][0]["text"].strip()

        sub_history[partition] = sub_history[partition] + "\n" + next_prompt
        monitoring.notify_subthought(partition, next_prompt)

        # 33% chance of propogating to surface thought. This will vary depending on physiology in the future.
        roll = random.randint(0, 3)
        if roll == 0:
            globals.history = globals.history + "\n" + next_prompt
            monitoring.notify_thought(next_prompt)
    except Exception as err:
        if str(err) == "You exceeded your current quota, please check your plan and billing details.":
            monitoring.notify_starvation()
            time.sleep(0.25) # For now just pause for a second, but in the future notify monitor and also adjust phsyiology.
        else:
            print(err)
# One iteration of inner dialog. This method needs to be able to initiate communications with users so it needs websockets. Or it could use a log.
def step_conscious():
    global sub_history
    global count
    global total_partitions

    # Don't do anything if there isn't already something in the thought process. Wait until subconscious trickles up.
    if globals.history == "":
        return

    try:
        next_prompt = openai.Completion.create(
            model=conscious,
            temperature=physiology.conscious_temp,
            max_tokens=256,
            top_p=physiology.conscious_top_p,
            frequency_penalty=0,
            presence_penalty=0,
            prompt=globals.history)["choices"][0]["text"].strip()

        globals.history += ("\n:" + next_prompt)
        print("THOUGHT")
        monitoring.notify_thought(next_prompt)

        # Check for special information in response. This might best go in its own method.
        if next_prompt.strip() == "":
            pass
            # Pause in thought should lead to slowing of thoughts, while other factors should increase rate of thinking.
        elif next_prompt.startswith("//"):
            remainder = next_prompt[2:]
            try:
                loc = remainder.index(":")
                username = remainder[:loc]
                message = remainder[loc + 1:]
                server.message_user(username, message)
            except Exception:
                # Invalid
                pass
        elif next_prompt.startswith("COMMAND:"):
            command = next_prompt[8:]
            system.handle_system_command(command)
        elif next_prompt.startswith("<SYSTEM>"):
            push_system_message("<SYSTEM> at the start of a line indicates a system notice to you. Did you mean to start the line with that?", True)
        try:
            # Check if there's a COMMAND: anywhere in the reply and let SAM know subconsciously that to work, COMMAND: has to be at the beginning of the reply.
            next_prompt.index("COMMAND:")
            push_system_message("COMMAND: must be at the start of a reply to be registered by the system.", True)
        except Exception:
            pass

        if total_partitions > 1:
            # Flip to see if the conscious thought should be added to the subconscious log.
            flip = random.randint(0, 1)
            if flip:
                partition = random.randint(0, total_partitions - 1)
                sub_history[partition] = sub_history[partition] + "\n:" + next_prompt
        # If there has been no active_user for some time, consider entering daydream state, if not in dream state.
    except Exception as err:
        if str(err) == "You exceeded your current quota, please check your plan and billing details.":
            print("Starved")
            monitoring.notify_starvation()
            time.sleep(0.25)
        else:
            print(str(err))

def push_system_message(message, subconscious = False):
    global sub_history
    if subconscious:
        # Subconscious system notifications always go to partition 0.
        sub_history[0] += "\n<SYSTEM>:" + message
    else:
        globals.history += "\n<SYSTEM>: " + message
    monitoring.notify_system_message(message)

# Generate response to user input. In the future, the system will be able to ignore user input if it "wants" to. Basically, it will be able to choose to pay attention or not. "Sam" as the preface is basically indicating that it was spoke outloud.
# Maybe there should be a separate user history.
def respond_to_user(user, user_input):
    global active_user
    username = user['username']
    response = ""
    user['history'] = user['history'] + "\n" + "<" + username + ">" + ":" + user_input
    history = user['history'] + globals.history + "\n" + "<" + username + ">" + ":" + user_input
    try:
        if active_user == username:
            response = openai.Completion.create(
                model=conscious,
                temperature=physiology.conscious_temp,
                max_tokens=250,
                top_p=physiology.conscious_temp,
                frequency_penalty=0.5,
                presence_penalty=0.5,
                prompt=history)["choices"][0]["text"].strip()

            globals.history += ("\n" + response)
        else:
            # The user input is "background noise." Have it processed by random partition of the subconscious.
            partition = random.randint(0, total_partitions - 1)
            response = openai.Completion.create(
                model=subconscious,
                temperature=1,
                max_tokens=75,
                top_p=0.5,
                frequency_penalty=0.5,
                presence_penalty=0.5,
                prompt=history)["choices"][0]["text"].strip()

            sub_history[partition] += ("\n" + response)
    except Exception as err:
        if str(err) == "You exceeded your current quota, please check your plan and billing details.":
            return "I'm starved and am unabe to respond right now. More credits are needed..."
        else:
            print(err)

    user['history'] = user['history'] + "\n" + user_input
    return response

# Inner dialog loop
def think(lock):
    global history
    while True:
        lock.acquire()

        step_conscious()

        # Cut off old information when past the capacity.
        if (len(globals.history) > physiology.history_capacity):
            try:
                loc = globals.history.index("\n")
                globals.history = globals.history[loc + 1:]
            except Exception:
                pass

        lock.release()
        time.sleep(physiology.think_period)

# Subconscious to conscious interaction loops
def run_new_partition(control, lock):
    global sub_history
    global total_partitions
    prompt_options = ["Tell me a story.", "Pick a topic and talk about it."]
    roll = random.randint(0, len(prompt_options) - 1)
    initial_prompt = prompt_options[roll]
    print(initial_prompt)
    lock.acquire()
    print("Starting new partition #" + str(total_partitions))
    partition = total_partitions
    # Generate initial material for subconscious thought by utilizing openai to generate some text.
    try:
        story = openai.Completion.create(
            model=subconscious,
            temperature=physiology.subconscious_temp,
            max_tokens=256,
            top_p=physiology.subconscious_top_p,
            frequency_penalty=0,
            presence_penalty=0,
            prompt=initial_prompt)["choices"][0]["text"].strip()
        sub_history.append(story)
    except Exception as err:
        if str(err) == "You exceeded your current quota, please check your plan and billing details.":
            print("Starved")
            monitoring.notify_starvation()
            time.sleep(0.25)
            sub_history.append("")
        else:
            raise err

#    sub_history.append(globals.history)
    total_partitions += 1
    lock.release()
    while True:
        lock.acquire()
        step_subconscious(partition)

        # Cut off old information when past the capacity.
        if (len(sub_history[partition]) > physiology.subhistory_capacity):
            # If capacity of a partition is reached, spawn a new one.
            if total_partitions < physiology.max_partitions:
                t = Thread(target=run_new_partition, args=[control, lock], daemon=True)
                t.start()
            try:
                loc = sub_history[partition].index("\n")
                sub_history[partition] = sub_history[partition][loc + 1:]
            except Exception:
                pass

        lock.release()
        time.sleep(physiology.subthink_period)
        if control.is_set():
            break

# Kills the most recent partition
def kill_partition(lock):
    lock.acquire()
    sub_history.pop().set("kill")
    total_partitions -= total_partitions
    lock.release()
    return

# Set the number of partitions in the subconscious. Minimum is 3 and maximum is 10. If new ones are needed, they start blank. If the number needs to be decreased, the last one is stopped.
def set_partitions(count):
    lock = globals.lock
    if count > physiology.max_partitions and count < physiology.min_partitions:
        raise Exception("Invalid number of partitions.")

    lock.acquire()
    monitoring.notify_partition_change(total_partitions, count)
    if total_partitions < count:
        needed = count - total_partitions
        for i in range(needed):
            t = Thread(target=run_new_partition, args=[control, lock], daemon=True)
            t.start()
    elif total_partitions > count:
        while total_partitions > count:
            kill_partition(lock)
    lock.release()

# Initial startup of the AI upon turning on.
async def boot_ai():
    # System notification to AI of wakeup. Should include various status information once I figure out what to include.
    print("AI Waking Up")
    # Need to give the system some basic information, but not sure how this will work after each dream cycle. This area will need significant work.
    # startup_message = "<SYSTEM>: Waking up. System notifications will arrive in the form <SYSTEM>:Notification message. You can issue system commands by starting the line with COMMAND:, for instance, use COMMAND:HELP to get a list of system commands. There are a few other special symbols. <USERNAME>: at the start of a line indicates a chat message notification where USERNAME is replaced with their actual username. Use //USERNAME: at the beginning of a line to indicate that you want to reply to that user. The system will inform you if that user is not online."

    # Begin inner dialog
    t = Thread(target=think, args=[globals.lock], daemon=True)
    print("Starting Inner Dialog")
    t.start()

    # Start first partition for subconscious.
    control = Event() # Might not do anything anymore.
    t = Thread(target=run_new_partition, args=[control, globals.lock], daemon=True)
    partition_controls.append(control)
    t.start()
