import openai
import time
import random
from threading import Thread
from threading import Event
import time

import globals
import physiology
import monitoring
import server
import system

# Maybe replace threading with aioschedule if possible.

sub_history = globals.sub_history

# Good to test code with the super cheap basic models, at least to check for errors. In the final version, the conscious and subconscious models might be different from each other to allow the inner workings of SAM's mind to be different from the conscious workings. The most recent trained model names will also have to be obtained.

conscious = "text-davinci-003"
subconscious = "text-davinci-003"

# The current user that SAM is listening to, if any, and set the time at which it was changed.
active_user = ""
active_last_changed = 0

waking_up = True
total_partitions = 0

def set_active_user(username):
    active_user = username
    active_last_changed = time.time()

# Count null thoughts to perform physiology changes, etc.
sub_null_thoughts = []
def step_subconscious():
    global sub_history
    global sub_null_thoughts
    partition = random.randint(0, total_partitions - 1)
    if sub_null_thoughts[partition] > physiology.max_subnulls:
        sub_null_thoughts[partition] = 0
        prompt = generate_sub_prompt(partition)
        sub_history[partition] += "\n" + prompt

    # Get next completion from the subconscious based on existing subconscious dialogue. Maybe add randomness by seeding with random thoughts.
    try:
        next_prompt = openai.Completion.create(
            model=subconscious,
            temperature=physiology.subconscious_temp,
            max_tokens=physiology.conscious_tokens,
            top_p=physiology.subconscious_top_p,
            frequency_penalty=0,
            presence_penalty=0,
            prompt=sub_history[partition])["choices"][0]["text"].strip()
        if len(next_prompt) == 0:
            # Ignore null thoughts.
            sub_null_thoughts[partition] += 1
            return
        print("SUB[" + str(partition) + "]: " + str(len(next_prompt)))

        sub_history[partition] = sub_history[partition] + "\n" + next_prompt
        if (len(sub_history[partition]) > physiology.subhistory_capacity):
            # If capacity of a partition is reached, spawn a new one.
            sub_history[partition] = sub_history[partition][physiology.subhistory_cut:]
            if total_partitions < physiology.max_partitions: add_new_partition()

        monitoring.notify_subthought(partition, next_prompt)

        if next_prompt.startswith("COMMAND:"):
            command = next_prompt[8:]
            system.handle_system_command(command)
            return
        elif next_prompt.startswith("<SYSTEM>"):
            push_system_message("<SYSTEM> at the start of a line indicates a system notice to you. Did you mean to start the line with that?", True)
            return
        try:
            # Check if there's a COMMAND: anywhere in the reply and let SAM know subconsciously that to work, COMMAND: has to be at the beginning of the reply.
            next_prompt.index("COMMAND:")
            push_system_message("COMMAND: must be at the start of a reply to be registered by the system.", True)
            return
        except Exception:
            pass

        # Determine if the thought propogates to the conscious.
        propogate = False
        if len(server.user_connections) != 0:
            # If there are active connecitons, propogation should be slower.
            length = len(next_prompt)
            roll = random.randint(0, 1)
            propogate = (roll == 0) and (length > physiology.min_subthought and length < physiology.max_subthought)
        else:
            # If nobody is connected, then there's a 90% chance that the thought will propogate.
            roll = random.randint(0, 9)
            propogate = (roll != 9)
        if propogate:
            globals.history = globals.history + "\n" + next_prompt
            monitoring.notify_thought(next_prompt)
    except Exception as err:
        if str(err) == "You exceeded your current quota, please check your plan and billing details.":
            print("Starved")
            monitoring.notify_starvation()
            time.sleep(0.25) # For now just pause for a second, but in the future notify monitor and also adjust phsyiology.
        else:
            print(err)

# One iteration of inner dialog. This method needs to be able to initiate communications with users so it needs websockets. Or it could use a log.
def step_conscious():
    global sub_history
    global count
    global total_partitions
    global waking_up

    # Don't do anything if there isn't already something in the thought process. Wait until subconscious trickles up and fills the conscious with thoughts.
    if len(globals.history) < (physiology.history_capacity / 2):
        print("Conscious Length: " + str(len(globals.history)))
        return

    waking_up = False # Useful signal for other parts of the program.

    try:
        next_prompt = openai.Completion.create(
            model=conscious,
            temperature=physiology.conscious_temp,
            max_tokens=physiology.conscious_tokens,
            top_p=physiology.conscious_top_p,
            frequency_penalty=0,
            presence_penalty=0,
            prompt=globals.history)["choices"][0]["text"].strip()

        print(len(next_prompt))
        if len(next_prompt) == 0:
            # Don't include zero length thoughts. But this might be used to slow down thinking, or enter daydream state.
            return
        globals.history += ("\n:" + next_prompt)
        print("THOUGHT: " + next_prompt + "\n")
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
# Maybe make use of confidence estimates to see if this completion should actually be said outloud or pushed to monologue.
# Maybe on chat close, or even just periodically, push a summary to the conscious layer.
def respond_to_user(user, user_input):
    global active_user # Rather than one active user the system can decide on having multiple active users.
    username = user['username']
    response = ""
    history = globals.history + "\n" + user['history'] +  "\n" + "<" + username + ">" + ":" + user_input
    globals.history += "\n" + "<" + username + ">" + ":" + user_input
    try:
        # For now, just keep all messages pushed to conscious.
        if True:
            response = openai.Completion.create(
                model=conscious,
                temperature=physiology.conscious_temp,
                max_tokens=physiology.userreply_tokens,
                top_p=physiology.conscious_temp,
                frequency_penalty=0.2,
                presence_penalty=0.2,
                prompt=history, stop = ".")["choices"][0]["text"].strip()

            globals.history += ("\n" + response)
        else:
            # The user input is "background noise." Have it processed by random partition of the subconscious.
            partition = random.randint(0, total_partitions - 1)
            response = openai.Completion.create(
                model=subconscious,
                temperature=1,
                max_tokens=physiology.conscious_tokens,
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

# Totally have to rewrite these next two methods to get it to work without threads.
def process_layers():
    print("Thought process starting...")
    while True:
        # Probably should loop through more than one subconscious partition, but that would make the monologue very slow.
        globals.lock.acquire()
        step_subconscious()
        globals.lock.release()

        globals.lock.acquire()
        step_conscious()
        globals.lock.release()

        globals.lock.acquire()
        # Cut off old information when past the capacity.
        if (len(globals.history) > physiology.history_capacity):
            globals.history = globals.history[physiology.history_cut:]
        globals.lock.release()
        time.sleep(physiology.think_period)

def generate_sub_prompt(partition):
    initial_prompt = ""
    if False: # For now skip system stuff until the basics work.
#    if partition == physiology.max_partitions:
        # Partition zero is the system interface partition so that's where this should go.
        initial_prompt = "<SYSTEM>: Waking up. System notifications will arrive in the form <SYSTEM>:Notification message. You can issue system commands by starting the line with COMMAND:, for instance, use COMMAND:HELP to get a list of system commands. There are a few other special symbols. <USERNAME>: at the start of a line indicates a chat message notification where USERNAME is replaced with their actual username. Use //USERNAME: at the beginning of a line to indicate that you want to reply to that user. The system will inform you if that user is not online."
    else:
        # Have to be careful, because some prompts give very short completions which can kill the subconscious thread.
        prompt_options = ["Tell me a story.", "Pick a topic and write a paragraph about it.", "Write a paragraph about what you want to do today."]
        roll = random.randint(0, len(prompt_options) - 1)
        initial_prompt = prompt_options[roll]
    return initial_prompt

# Subconscious to conscious interaction loops
def add_new_partition():
    global sub_history
    global sub_null_thoughts
    global total_partitions
    partition = total_partitions

    initial_prompt = generate_sub_prompt(partition)

    # Generate initial material for subconscious thought by utilizing openai to generate some text.
    try:
        initial = openai.Completion.create(
            model=subconscious,
            temperature=physiology.subconscious_temp,
            max_tokens=physiology.initialize_tokens,
            top_p=physiology.subconscious_top_p,
            frequency_penalty=0,
            presence_penalty=0,
            prompt=initial_prompt)["choices"][0]["text"].strip()
        sub_history.append(initial)
#        print("Initial: " + initial)
    except Exception as err:
        if str(err) == "You exceeded your current quota, please check your plan and billing details.":
            print("Starved")
            monitoring.notify_starvation()
            time.sleep(0.25)
            sub_history.append("")
        else:
            raise err

    print("Adding new partition #" + str(total_partitions))
    sub_null_thoughts.append(0)
    total_partitions += 1

# Kills the most recent partition: Not fixed
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
            add_new_partition()
    elif total_partitions > count:
        while total_partitions > count:
            kill_partition(lock)
    lock.release()

# Initial startup of the AI upon turning on.
async def boot_ai():
    # System notification to AI of wakeup. Should include various status information once I figure out what to include.
    print("AI Waking Up")
    # Need to give the system some basic information, but not sure how this will work after each dream cycle. This area will need significant work.

    add_new_partition()
    t = Thread(target=process_layers, args=[], daemon=True)
    t.start()
