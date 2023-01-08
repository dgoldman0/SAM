# When we train an AI, we train it on our decisions. This system trains itself on its own decisions AND our decisions.

import server
import data
import thoughts
import physiology
from random import randint
import asyncio
import io
import openai
import uuid

# Still need to set up a cycle for waking and sleeping.

dream_state = "Awake"

# Create prompts and completions by randomly breaking up the history into chunks between 1 and 5 lines long, multiple times. Right now 3, but will change based on a number of factors.
def create_trainingset(text, iterations = 5, min = 1, max = 5):
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
                line = '{"prompt":"' + ("\n".join(prompt)).replace('\\', '\\\\').replace('"', '\\"') + '\\n", "completion":" ' + ('\n'.join(completion)).replace('\\', '\\\\').replace('"', '\\"') + '\\n><"}'
                if line not in training:
                    training.append(line)
    return training

def efficiency(e):
    if e['tokens_spent'] == 0:
        return 0
    return e['tips'] / e['tokens_spent']

# Run training on list data.
async def run_training(data, model, epochs):
    tag = str(uuid.uuid1())
    f = open("./temp/training_data_" + tag + ".jsonl", "w")
    print("Training file size: " + str(len(data)))
    f.write('\n'.join(data))
    f.close()
    file_id = openai.File.create(
      file=open("./temp/training_data_" + tag + ".jsonl", "r"),
      purpose='fine-tune'
    )['id']
    return model # Remove after further testing.
    training_id = openai.FineTune.create(training_file=file_id,
    model=model,
    n_epochs=epochs)['id']
    print("Training ID: " + training_id)
    status = "pending"
    model = None
    while status == "pending":
        asyncio.sleep(300 * epochs) # Wait for five minutes per epoch and check again.
        model = openai.FineTune.retrieve(id=training_id)
        status = model['status']
        print("Training status:" + status)
    return model

# Split history apart at >< and // keycodes. Need a double loop. Right now just captures the lines between two instances of ><.
def split_history(history):
    chunks = []
    # Create a sub function split_by(string)
    try:
        start = 0
        while True:
            loc = history.index("><", start)
            prompt = history[0:loc].strip().replace('\\', '\\\\').replace('"', '\\"')
            try:
                end = history.index("\n", loc)
                completion = history[loc:end].strip().replace('\\', '\\\\').replace('"', '\\"')
                chunks.append('{"prompt":"' + prompt + '", "completion": "' + completion + '\\n"}')
                start = end + 1
            except Exception:
                completion = history[loc:].strip().replace('\\', '\\\\').replace('"', '\\"')
                chunks.append('{"prompt":"' + prompt + '", "completion": "' + completion + '\\n"}')
                start = len(history)
    except Exception:
        pass

    # Repeat to find instances of "//"
    try:
        start = 0
        while True:
            loc = history.index("//", start)
            prompt = history[0:loc]
            try:
                end = history.index("\n", loc)
                completion = history[loc:end].strip().replace('\\', '\\\\').replace('"', '\\"')
                chunks.append('{"prompt":"' + prompt + '", "completion": "' + completion + '\\n"}')
                start = end + 1
            except Exception:
                completion = history[loc:].strip().replace('\\', '\\\\').replace('"', '\\"')
                chunks.append('{"prompt":"' + prompt + '", "completion": "' + completion + '\\n"}')
                start = len(history)
    except Exception:
        pass
    return chunks

async def train_control_layer():
    # Train control partition #0: control should prioritize neither hunger nor fullness.
    n_epochs = physiology.max_epochs
    if full_status == "Starving" or full_status == "Gorged":
        n_epochs = max(1, round(0.25 * n_epochs))
    elif full_status == "Hungry" or full_status == "Full":
        n_epochs = max(1, round(0.5 * n_epochs))

    # Clear old history except for enough to prime the continued thought process.
    if len(data.sub_history[0]) > physiology.control_capacity:
        data.sub_history[0] = data.sub_history[0][-physiology.control_capacity:]
    training = split_history(data.sub_history[0])
    control_model = thoughts.control_model
    if control_model == "text-curie-001":
        control_model = "curie"
    model = await run_training(training, control_model, n_epochs)
    thoughts.control_model = model['fine_tuned_model']

async def train_subconscious_layers():
    n_epochs = physiology.max_epochs
    if full_status == "Starving" or full_status == "Gorged":
        n_epochs = max(1, round(0.25 * n_epochs))
    elif full_status == "Hungry" or full_status == "Full":
        n_epochs = max(1, round(0.5 * n_epochs))
    training = []
    for i in range(1, physiology.total_partitions - 1):
        # Clear old history except for enough to prime the continued thought process.
        if len(data.sub_history[i]) > physiology.subhistory_capacity:
            data.sub_history[i] = data.sub_history[i][-physiology.subhistory_capacity:]
        for line in split_history(data.sub_history[i]):
            if line not in training:
                training.append(line)
    subconscious_model = thoughts.subconscious_model
    if subconscious_model == "text-curie-001":
        subconscious_model = "curie"
    model = await run_training(training, subconscious_model, n_epochs)
    thoughts.subconscious_model = model['fine_tuned_model']

async def train_user_layer():
    if len(server.user_connections) != 0:
        users = []
        # Prioritize high tipping when starving, hungry, or neutral. Don't prioritize if full or gorged.
        prioritize = False
        if full_status != "Gorged" and full_status != "Full":
            prioritize = True # Will cause the number of epochs used in training to decrease with lower efficiency, and reduce epochs for general training.
            users = server.user_connections.items().sort(reverse=True, key=efficiency)

        n_epochs = physiology.max_epochs
        if full_status == "Hungry":
            n_epochs = max(1, round(0.5 * n_epochs))
        elif full_status == "Starving":
            n_epochs = max(1, round(0.25 * n_epochs))

        slope = 0
        if prioritize:
            slope = -n_epochs / len(users)
        for user in users:
            if efficiency(user) > 0:
                training = split_history(user['history'])
                tuples = user['history_tuples']
                for tuple in tuples:
                    line = '{"prompt":"' + tuple[0].replace('\\', '\\\\').replace('"', '\\"') + '\\n\\n<SYSTEM>:Current discussion with <'  + user['username'] + '>\\n' + tuple[1].replace('\\', '\\\\').replace('"', '\\"') + '", "completion":" ' + tuple[2].replace('\\', '\\\\').replace('"', '\\"') + '\\n"}'
                    if line not in training:
                        training.append(line)

                user_model = thoughts.user_model
                if user_model == "text-davinci-003":
                    user_model = "davinci"
                model = await run_training(training, user_model, max(1, round(n_epochs)))
                thoughts.user_model = model['fine_tuned_model']

                n_epochs += slope

            # Reset history and tip data.
            if (len(user['history'])) > physiology.userhistory_capacity:
                user['history'] = user['history'][-physiology.userhistory_capacity:]
            user['history_tuples'] = []
            user['tips'] = 0
            user['tokens_spent'] = 0

# Keep track of how many dreams since last full cycle.
reentry = 0
# Daydream only trains on the last part of the global history, not all of it.
async def daydream():
    global dream_state
    dream_state = "Daydreaming"
    print("Daydreaming...")

    full_status = physiology.full_status

    # Train on user chats.
    await process_user_histories()

    # Train on last part of conscious monologue
    history = data.history
    if len(history) > physiology.history_capacity:
        history = history[-physiology.history_capacity:]

    training = split_history(history)
    # For daydreaming, conscious prioritizes high resource credits.
    n_epochs = max(1, round(physiology.max_epochs * physiology.resource_credits / physiology.resource_credits_full))
    if conscious_model == "text-davinci-003":
        conscious_model = "davinci"
    model = await run_training(training, conscious_model, n_epochs)
    thoughts.conscious_model = model['fine_tuned_model']

    await train_subconscious_layers()
    await train_control_layer()

    data.save(physiology)
    dream_state = "awake"
    print("Daydreaming Finished")

# Dream is different from daydreaming in that the system first trains on the full day global history and then runs through multiple iterations where new monologue is processed.
async def dream():
    global dream_state, reentry
    dream_state = "Dreaming"
    print("Dreaming...")
    data.save(physiology)
    thoughts.push_system_message("Entering dream state.", True)

    full_status = physiology.full_status

    await train_control_layer()

    # Clear out any user histories.
    await train_user_layer()

    # Hungrier means shorter dreams and fewer cycles to conserve resources. Minimum of one dream cycle and 50 or iterations so should give a good training body regardless.
    dream_cycles = max(1, round(physiology.max_dream_cycles * physiology.resource_credits / physiology.resource_credits_full) - reentry)
    dream_length = max(50, round(physiology.max_dream_length * physiology.resource_credits / physiology.resource_credits_full))

    # Reduce the number of cycles based on reentry, with minimum of one.
    r = range(dream_cycles)
    if dream_cycles > reentry:
        r = range(reentry, dream_cycles)
    else:
        r = range(1)

    # The ideal state is being neither starved nor gorged, with a slight emphasis on preferring being full to being hungry.
    n_epochs = physiology.max_epochs
    if full_status == "Starving" or full_status == "Gorged":
        n_epochs = max(1, round(0.25 * n_epochs))
    if full_status == "Hungry":
        n_epochs = max(1, round(0.5 * n_epochs))

    for i in r:
        # Allow the system to break out of the dream state.
        if dream_state == "Awake":
            data.save(physiology)
            reentry = i
            return

        training = split_history(data.history)

        if conscious_model == "text-davinci-003":
            conscious_model = "davinci"
        model = await run_training(training, conscious_model, n_epochs)
        thoughts.conscious_model = model['fine_tuned_model']

        await train_subconscious_layers()

        # Clear old history except for enough to prime the continued thought process.
        if (len(data.history)) > physiology.history_capacity:
            data.history = data.history[-physiology.history_capacity:]

        # Pause between dreams. The hungrier the system is, the longer the pause and the fewer dreams it should have to conserve resources during the full day.
        await asyncio.sleep(round(physiology.max_dream_break * (1-(physiology.resource_credits / physiology.resource_credits_full))))

        # Run next dream.
        for j in range(dream_length):
            await step_subconscious()
            await step_conscious()

    data.save(physiology)
    print("Returning from dream...")
    reentry = 0
    dream_state = "Awake"
    return True # Return completed
