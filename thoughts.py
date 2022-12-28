import openai
import time
import random
from threading import Thread
from threading import Event
import time
import asyncio

import globals
import physiology
import monitoring
import server
import system

# Eventually it might possibly make sense to replace a single string with a list of strings, to make it easier to cut up by prompt and completion.
sub_history = globals.sub_history

# Good to test code with the super cheap basic models, at least to check for errors. In the final version, the conscious and subconscious models might be different from each other to allow the inner workings of SAM's mind to be different from the conscious workings. The most recent trained model names will also have to be obtained.

conscious = "text-davinci-003"
subconscious = "text-davinci-003"

# The current user that SAM is listening to, if any, and set the time at which it was changed.
active_user = ""
active_last_changed = 0

waking_up = True

def set_active_user(username):
    active_user = username
    active_last_changed = time.time()

# Count null thoughts to perform physiology changes, etc.
sub_null_thoughts = []

# Should the subconscious be able to push voiced?
async def step_subconscious():
    global sub_history
    global sub_null_thoughts
    partition = random.randint(0, globals.total_partitions - 1)
    if sub_null_thoughts[partition] > physiology.max_subnulls:
        sub_null_thoughts[partition] = 0
        prompt = generate_sub_prompt(partition)
        sub_history[partition] += "\n" + prompt

    # Get next completion from the subconscious based on existing subconscious dialogue. Maybe add randomness by seeding with random thoughts.
    try:
        openai_response = openai.Completion.create(
            model=subconscious,
            temperature=physiology.subconscious_temp,
            max_tokens=physiology.conscious_tokens,
            top_p=physiology.subconscious_top_p,
            frequency_penalty=0,
            presence_penalty=0,
            prompt=sub_history[partition])
        next_prompt = openai_response["choices"][0]["text"].strip()
        physiology.resource_credits -= openai_response["usage"]["total_tokens"]

        if len(next_prompt) == 0:
            sub_null_thoughts[partition] += 1
            return

        print("SUB[" + str(partition) + "]: " + str(len(next_prompt)))

        sub_history[partition] = sub_history[partition] + "\n" + next_prompt
        if (len(sub_history[partition]) > physiology.subhistory_capacity):
            # If capacity of a partition is reached, spawn a new one.
            sub_history[partition] = sub_history[partition][physiology.subhistory_cut:]
            if globals.total_partitions < physiology.max_partitions:
                # If the number of partitions is less than the number of partitions that need to be seeded, then seed, otherwise start blank.
                add_new_partition(globals.total_partitions < physiology.seeded_partitions + 1)

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

        # Determine if the thought propogates to the conscious. These values will be changed by physiology at some point.
        propogate = False
        roll = random.randint(0, 9)
        if len(server.user_connections) != 0:
            # If there are active connecitons, propogation should be slower.
            length = len(next_prompt)
            propogate = (roll < 2)
        else:
            # If nobody is connected, subconscious thoughts can propogate faster, especially when the history is not close to full.
            if len(globals.history) < (physiology.history_capacity * 3/4):
                propogate = (roll != 9)
            else:
                propogate = (roll < 5)
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
async def step_conscious():
    global sub_history
    global count
    global waking_up

    # Don't do anything if there isn't already something in the thought process. Wait until subconscious trickles up and fills the conscious with thoughts.
    if len(globals.history) < (physiology.history_capacity):
        print("Conscious Length: " + str(len(globals.history)))
        return

    if waking_up:
        print("Awake!")
        waking_up = False
        if globals.first_load:
            globals.save(physiology)

    try:
        openai_response = openai.Completion.create(
            model=conscious,
            temperature=physiology.conscious_temp,
            max_tokens=physiology.conscious_tokens,
            top_p=physiology.conscious_top_p,
            frequency_penalty=0,
            presence_penalty=0,
            prompt=globals.history)
        next_prompt = openai_response["choices"][0]["text"].strip()
        physiology.resource_credits -= openai_response["usage"]["total_tokens"]

        if len(next_prompt) == 0:
            # Don't include null thoughts.
            return

        globals.history += ("\n" + next_prompt)
#        print("THOUGHT: " + next_prompt + "\n")
        monitoring.notify_thought(next_prompt)

        # Check for special information in response. This might best go in its own method.
        if next_prompt.startswith("//"):
            remainder = next_prompt[2:]
            try:
                loc = remainder.index(":")
                username = remainder[:loc]
                message = remainder[loc + 1:]
                await server.message_user(username, message)
            except Exception:
                # Invalid
                pass

        if globals.total_partitions > 1:
            # Flip to see if the conscious thought should be added to the subconscious log.
            flip = random.randint(0, 1)
            if flip:
                partition = random.randint(0, globals.total_partitions - 1)
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

    # Maybe only do the last segment of the global history so it doesn't overpower.
    try:
        # For now, just keep all messages pushed to conscious.
        if True:
            # Summarize the concscious history to make it easier to process with user input.
            user['history'] += ("\n" + "<" + username + ">" + ":" + user_input)
            history = "Current thoughts:\n" + globals.history + "\n\nCurrent discussion with " + username + ":\n" + user['history']
            openai_response = openai.Completion.create(
                model=conscious,
                temperature=physiology.conscious_temp,
                max_tokens=physiology.userreply_tokens,
                top_p=physiology.conscious_temp,
                frequency_penalty=0.1,
                presence_penalty=0.1,
                prompt=history)
            response = openai_response["choices"][0]["text"].strip()
            physiology.resource_credits -= openai_response["usage"]["total_tokens"]

            print("Response: " + response)
            globals.history += ("\<" + username + "> :" + user_input)
            if len(response) > 0:
                globals.history += ("\n//" + username + ":" + response)
                user['history'] += ("\n//" + username + ":" + response)
            else:
                # Ignore null responses.
                print("Null response caused by: " + history + "\n")
        else:
            # The user input is "background noise." Have it processed by random partition of the subconscious.
            partition = random.randint(0, globals.total_partitions - 1)
            openai_response = openai.Completion.create(
                model=subconscious,
                temperature=subconscious_temp,
                max_tokens=physiology.conscious_tokens,
                top_p=subconscious_top_p,
                frequency_penalty=0.1,
                presence_penalty=0.1,
                prompt=history)
            response = openai_response["choices"][0]["text"].strip()
            physiology.resource_credits -= openai_response["usage"]["total_tokens"]

            sub_history[partition] += ("\nMessage from " + username + ":" + user_input)
            if len(response) > 0:
                sub_history[partition] += ("\n//" + username + ":" + response)
        # Need to slice off old history as with other histories.
    except Exception as err:
        if str(err) == "You exceeded your current quota, please check your plan and billing details.":
            return "I'm starved and am unabe to respond right now. More credits are needed..."
        else:
            print(err)

    return response

# Totally have to rewrite these next two methods to get it to work without threads.
async def process_layers():
    print("Thought process starting...")
    while True:
        # Probably should loop through more than one subconscious partition, but that would make the monologue very slow.
        # Check for physiology and other system reports, before going through subconscious. While this will be built in, the subconscious should be able to override in time. It might "know better" than the developer as to how to perform.
        physiology.review()
        # Reduce conscious and subconscious activity to zero coma state.
        if physiology.resource_credits > 0.05 * physiology.resource_credits_full:
            await step_subconscious()
            if physiology.resource_credits > 0.1 * physiology.resource_credits_full:
                await step_conscious()
                # Cut off old information when past the capacity.
                if (len(globals.history) > physiology.history_capacity):
                    globals.history = globals.history[physiology.history_cut:]

        await asyncio.sleep(physiology.think_period)

def generate_sub_prompt(partition):
    initial_prompt = ""
    if partition == 0:
        # Partition zero is the system interface partition so that's where this should go.
        initial_prompt = "<SYSTEM>: Waking up. System notifications will arrive in the form <SYSTEM>:Notification message. You can issue system commands by starting the line with COMMAND:, for instance, use COMMAND:HELP to get a list of system commands. There are a few other special symbols. <USERNAME>: at the start of a line indicates a chat message notification where USERNAME is replaced with their actual username. Use //USERNAME: at the beginning of a line to indicate that you want to reply to that user. The system will inform you if that user is not online."
    else:
        # Have to be careful, because some prompts give very short completions which can kill the subconscious thread.
        prompt_options = ["Tell me a story.", "Pick a topic and write a paragraph about it.", "Write a paragraph about what you want to do today."]
        roll = random.randint(0, len(prompt_options) - 1)
        initial_prompt = prompt_options[roll]
    return initial_prompt

# Subconscious to conscious interaction loops
def add_new_partition(generate = True):
    global sub_history
    global sub_null_thoughts
    partition = globals.total_partitions
    if generate:
        initial_prompt = generate_sub_prompt(partition)

        # Generate initial material for subconscious thought by utilizing openai to generate some text.
        try:
            openai_response = openai.Completion.create(
                model=subconscious,
                temperature=physiology.subconscious_temp,
                max_tokens=physiology.initialize_tokens,
                top_p=physiology.subconscious_top_p,
                frequency_penalty=0,
                presence_penalty=0,
                prompt=initial_prompt)
            initial = openai_response["choices"][0]["text"].strip()
            physiology.resource_credits -= openai_response["usage"]["total_tokens"]

            sub_history.append(initial)
        except Exception as err:
            if str(err) == "You exceeded your current quota, please check your plan and billing details.":
                print("Starved")
                monitoring.notify_starvation()
                time.sleep(0.25)
                sub_history.append("")
            else:
                raise err
    else:
        sub_history.append("")

    print("Adding new partition #" + str(globals.total_partitions))
    sub_null_thoughts.append(0)
    globals.total_partitions += 1

# Kills the most recent partition: Not fixed
def kill_partition():
    sub_history.pop().set("kill")
    globals.total_partitions -= globals.total_partitions
    return

# Set the number of partitions in the subconscious. Minimum is 3 and maximum is 10. If new ones are needed, they start blank. If the number needs to be decreased, the last one is stopped.
def set_partitions(count):
    if count > physiology.max_partitions and count < physiology.min_partitions:
        raise Exception("Invalid number of partitions.")

    monitoring.notify_partition_change(globals.total_partitions, count)
    if globals.total_partitions < count:
        needed = count - globals.total_partitions
        for i in range(needed):
            add_new_partition()
    elif globals.total_partitions > count:
        while globals.total_partitions > count:
            kill_partition()

# Initial startup of the AI upon turning on.
async def boot_ai():
    # System notification to AI of wakeup. Should include various status information once I figure out what to include.
    print("AI Waking Up")
    # Need to give the system some basic information, but not sure how this will work after each dream cycle. This area will need significant work.

    # Check if there are already a full number of partitions. If not, add.
    if globals.total_partitions < physiology.max_partitions:
        add_new_partition()
    else:
        print("Loaded from previous state...")
    await process_layers()
