import openai
import time
import random
from threading import Thread
from threading import Event
import time
import asyncio

import data
import physiology
import monitoring
import server
import system
import learning

# Eventually it might possibly make sense to replace a single string with a list of strings, to make it easier to cut up by prompt and completion.
sub_history = data.sub_history

# Good to test code with the super cheap basic models, at least to check for errors. In the final version, the conscious and subconscious models might be different from each other to allow the inner workings of SAM's mind to be different from the conscious workings. The most recent trained model names will also have to be obtained.

user_model = "text-davinci-003"
conscious_model = "text-davinci-003"
# Subconscious and control may be able to do well enough with curie as the model.
subconscious_model = "text-curie-001"
control_model = "text-curie-001"

# The current user that SAM is listening to, if any, and set the time at which it was changed.
active_user = ""
active_last_changed = 0

waking_up = True

# Should check to see if the system works with stop = \n in place now.

def set_active_user(username):
    active_user = username
    active_last_changed = time.time()

# Count null thoughts to perform physiology changes, etc.
sub_null_thoughts = []

# Should the subconscious be able to push voiced?
async def step_subconscious(partition = None):
    global sub_history
    global sub_null_thoughts
    if partition is None:
        partition = random.randint(1, data.total_partitions - 1)
    if sub_null_thoughts[partition] > physiology.max_subnulls:
        sub_null_thoughts[partition] = 0
        prompt = generate_sub_prompt(partition)
        sub_history[partition] += "\n><" + prompt

    capacity = physiology.subhistory_capacity
    if partition == 0:
        capacity = physiology.control_capacity
    prompt = sub_history[partition]
    if (len(prompt)) > capacity:
        prompt = prompt[-capacity:]
    # Get next completion from the subconscious based on existing subconscious dialogue. Maybe add randomness by seeding with random thoughts.
    model = subconscious_model
    if partition == 0:
        model = control_model
    try:
        openai_response = openai.Completion.create(
            model=model,
            temperature=physiology.subconscious_temp,
            max_tokens=physiology.subconscious_tokens,
            top_p=physiology.subconscious_top_p,
            frequency_penalty=0,
            presence_penalty=0,
            prompt=prompt,
            stop="\n><")
        next_prompt = openai_response["choices"][0]["text"].strip()
        physiology.resource_credits -= openai_response["usage"]["total_tokens"]

        if len(next_prompt) == 0:
            sub_null_thoughts[partition] += 1
            return

        # This replacement will prevent some confusion between system generated fake keycodes and real ones.
        next_prompt = next_prompt.replace('\n>', '\n%3E').replace('\n<', '\n%3C').replace('\nCOMMAND:', '\nCOMMAND%3A')
        sub_history[partition] = sub_history[partition] + "\n><" + next_prompt
        if (len(sub_history[partition]) > physiology.subhistory_capacity) and data.total_partitions < physiology.max_partitions:
            # If the number of partitions is less than the number of partitions that need to be seeded, then seed, otherwise start blank.
            add_new_partition(data.total_partitions < physiology.seeded_partitions + 1)

        monitoring.notify_subthought(partition, next_prompt)

        # Commands can only come from control partition.
        if partition == 0 and next_prompt.startswith("COMMAND:"):
            command = next_prompt[8:]
            system.handle_system_command(command, True)
            return

        # Decide if the thought propogates to the conscious. These values will be changed by physiology at some point.
        propogate = False
        roll = random.randint(0, 9)
        if len(server.user_connections) != 0:
            # If there are active connecitons, propogation should be slower.
            length = len(next_prompt)
            propogate = (roll < 2)
        else:
            # If nobody is connected, subconscious thoughts can propogate faster, especially when the history is not close to full.
            if len(data.history) < (physiology.history_capacity * 3/4):
                propogate = (roll != 9)
            else:
                propogate = (roll < 5)
        if propogate:
            data.history = data.history + "\n<>" + next_prompt
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
    print("Conscious Length: " + str(len(data.history)))
    if len(data.history) < (physiology.history_capacity):
        return

    if waking_up:
        print("Awake!")
        waking_up = False
        if data.first_load:
            data.save(physiology)

    prompt = data.history
    if (len(prompt)) > physiology.history_capacity:
        prompt = prompt[-physiology.history_capacity:]
    try:
        openai_response = openai.Completion.create(
            model=conscious_model,
            temperature=physiology.conscious_temp,
            max_tokens=physiology.conscious_tokens,
            top_p=physiology.conscious_top_p,
            frequency_penalty=0,
            presence_penalty=0,
            prompt=prompt,
            stop='\n><')
        next_prompt = openai_response["choices"][0]["text"].strip()
        physiology.resource_credits -= openai_response["usage"]["total_tokens"]

        if len(next_prompt) == 0:
            # Don't include null thoughts.
            return

        next_prompt = next_prompt.replace('\n/', '\n%2F').replace('\n|', '\n%7C%').replace('\n>', '\n%3E').replace('\n<', '\n%3C').replace('\nCOMMAND:', '\nCOMMAND%3A')

        # Check for special information in response. This might best go in its own method.
        if next_prompt.startswith("//"):
            data.history += ('\n' + next_prompt)
            remainder = next_prompt[2:]
            try:
                loc = remainder.index(":")
                username = remainder[:loc]
                message = remainder[loc + 1:]
                await server.message_user(username, message)
            except Exception:
                pass
        else:
            data.history += ("\n><" + next_prompt)

        monitoring.notify_thought(next_prompt)
        if data.total_partitions > 1:
            # Always add cosncious thought to control log.
            sub_history[0] = sub_history[partition] + "\n<>:" + next_prompt
            # Flip to see if the conscious thought should be added to the subconscious log.
            flip = random.randint(0, 1)
            if flip:
                partition = random.randint(1, data.total_partitions - 1)
                sub_history[partition] = sub_history[partition] + "\n<>:" + next_prompt

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
        data.history += "\n<SYSTEM>: " + message
    monitoring.notify_system_message(message)

# Generate response to user input. In the future, the system will be able to ignore user input if it "wants" to. Basically, it will be able to choose to pay attention or not. "Sam" as the preface is basically indicating that it was spoke outloud.
# Maybe make use of confidence estimates to see if this completion should actually be said outloud or pushed to monologue.
# Maybe on chat close, or even just periodically, push a summary to the conscious layer.
def respond_to_user(user, user_input):
    global active_user # Rather than one active user the system can decide on having multiple active users.
    username = user['username']
    response = ""

    # Maybe only do the last segment of the global history so it doesn't overpower.
    user_input = user_input.replace('\n|', '\n%7C').replace('\n<', '\n%3C').replace('\n>', '\n%3E')
    try:
        # For now, just keep all messages pushed to conscious. Will go to subconscious when daydreaming.
        if learning.dream_state != "Dreaming" and learning.dream_state != "Daydreaming":
            # Summarize the concscious history to make it easier to process with user input.
            user['history'] += ("\n" + "<" + username + ">" + ":" + user_input)
            hist_cut = data.history
            user_hist_cut = user['history']
            if (len(hist_cut)) > physiology.history_capacity:
                hist_cut = hist_cut[-physiology.history_capacity:]
            if (len(user_hist_cut)) > physiology.userhistory_capacity:
                user_hist_cut = user_hist_cut[-physiology.userhistory_capacity:]
            history = "<SYSTEM>:Current thoughts:\n" + hist_cut + "\n\n<SYSTEM>:Current discussion with " + username + ":\n" + user_hist_cut
            openai_response = openai.Completion.create(
                model=user_model,
                temperature=physiology.conscious_temp,
                max_tokens=physiology.userreply_tokens,
                top_p=physiology.conscious_temp,
                frequency_penalty=0.1,
                presence_penalty=0.1,
                prompt=history,
                stop="\n><")
            response = openai_response["choices"][0]["text"].strip()
            response = response.replace('\n|', '\n%7C').replace('\n<', '\n%3C').replace('\n>', '\n%3E')
            tokens = openai_response["usage"]["total_tokens"]
            physiology.resource_credits -= tokens
            user['tokens_spent'] += tokens
            print("Response: " + response)
            data.history += ("\<" + username + ">:" + user_input)
            if len(response) > 0:
                data.history += ("\n||" + username + ":" + response)
                user['history'] += ("\n><" + username + ":" + response)
                user['history_tuples'].append([hist_cut, user_hist_cut, response, physiology.resource_credits])
            else:
                # Ignore null responses.
                print("Null response caused by: " + history + "\n")
        else:
            # Not paying attention, so push to control subconscious layer for processing.
            data.sub_history[0] += ("\<" + username + ">:" + user_input)
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
        # Always run through the control system and review.
        await step_subconscious(0)
        physiology.review()
        # Reduce conscious and subconscious activity to zero coma state, and also don't iterate when dreaming, since that would interfere.
        if physiology.resource_credits > 0.05 * physiology.resource_credits_full and learning.dream_state != "Dreaming":
            await step_subconscious()
            if physiology.resource_credits > 0.1 * physiology.resource_credits_full:
                await step_conscious()

        await asyncio.sleep(physiology.think_period)

def generate_sub_prompt(partition):
    initial_prompt = ""
    if partition == 0:
        # Partition zero is the system interface partition so that's where this should go.
        initial_prompt = "<SYSTEM>:Waking up. System notifications will arrive in the form <SYSTEM>:Notification message. You can issue system commands by starting the line with COMMAND:, for instance, use COMMAND:HELP to get a list of system commands. There are a few other special symbols. <USERNAME>: at the start of a line indicates a chat message notification where USERNAME is replaced with their actual username. Use //USERNAME: at the beginning of a line to indicate that you want to reply to that user. The system will inform you if that user is not online."
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
    partition = data.total_partitions
    if generate:
        initial_prompt = "><" + generate_sub_prompt(partition)

        # Generate initial material for subconscious thought by utilizing openai to generate some text.
        try:
            openai_response = openai.Completion.create(
                model=subconscious_model,
                temperature=physiology.subconscious_temp,
                max_tokens=physiology.initialize_tokens,
                top_p=physiology.subconscious_top_p,
                frequency_penalty=0,
                presence_penalty=0,
                prompt=initial_prompt,
                stop="\n><")
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

    print("Adding new partition #" + str(data.total_partitions))
    sub_null_thoughts.append(0)
    data.total_partitions += 1

# Kills the most recent partition: Not fixed
def kill_partition():
    sub_history.pop().set("kill")
    data.total_partitions -= data.total_partitions
    return

# Set the number of partitions in the subconscious. Minimum is 3 and maximum is 10. If new ones are needed, they start blank. If the number needs to be decreased, the last one is stopped.
def set_partitions(count):
    if count > physiology.max_partitions and count < physiology.min_partitions:
        raise Exception("Invalid number of partitions.")

    monitoring.notify_partition_change(data.total_partitions, count)
    if data.total_partitions < count:
        needed = count - data.total_partitions
        for i in range(needed):
            add_new_partition()
    elif data.total_partitions > count:
        while data.total_partitions > count:
            kill_partition()

# Initial startup of the AI upon turning on.
async def boot_ai():
    # System notification to AI of wakeup. Should include various status information once I figure out what to include.
    print("AI Waking Up")
    # Need to give the system some basic information, but not sure how this will work after each dream cycle. This area will need significant work.

    # Check if there are already a full number of partitions. If not, add.
    if data.total_partitions < physiology.max_partitions:
        add_new_partition()
    else:
        print("Loaded from previous state...")
    await process_layers()
