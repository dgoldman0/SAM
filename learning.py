# Give preference to training sets that yield more credits, when the system is hungry, but don't when it isn't.
# When we train an AI, we train it on our decisions. This system trains itself on its own decisions AND our decisions.
# Drop blank histories. Rank by amount paid / line generated, so a short conversation which brings in a lot is really good.

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

# Need to adjust for initial learning process because the model chosen should be "davinci" by itself, I think.
dream_state = "Awake"

# Create prompts and completions by randomly breaking up the history into chunks between 1 and 5 lines long, multiple times. Right now 3, but will change based on a number of factors.
def split(text, iterations = 5, min = 1, max = 5):
    training = []
    for in in range(iterations):
        cur = 0
        while cur < len(text) - 2:
            prompt = []
            completion = []
            prompt_size = randint(min,max)
            completion_size = randint(min, max)
            if len(history) > cur + prompt_size + completion_size:
                prompt = text[cur:cur + prompt_size]
                completion = text[cur + prompt_size:cur + prompt_size + completion_size]
                cur += (prompt_size + completion_size)
            else:
                prompt = history[cur:-1]
                completion = history[-1]
                cur = len(history)
            line = '{"prompt":' + "\\n".join(prompt) + '\\n, "completion":' '\\n'.join(completion) + "\\n}"]
            if line is not in training:
                training.append(line)
    return training

def efficiency(e):
    if e['tokens_spent'] == 0:
        return 0
    return e['tips'] / e['tokens_spent']

# Run training on list data.
async def run_training(data, model, epochs):
    tag = uuid.uuid1()
    f = open("./temp/training_data_" + tag + ".jsonl", "wb")
    print("Training file size: " + str(len(training)))
    f.write('\n'.join(training))
    f.close()
    file_id = openai.File.create(
      file=open("./temp/training_data_" + tag + ".jsonl", "rb"),
      purpose='fine-tune'
    )['id']
    training_id = openai.FineTune.create(training_file=file_id
    model=model,
    n_epochs=epochs)['id']
    print("Training ID: " + training_id)
    status = "pending"
    model = None
    while status == "pending":
        asyncio.sleep(300 * n_epochs) # Wait for five minutes per epoch and check again.
        model = openai.FineTune.retrieve(id=training_id)
        status = model['status']
        print("Training status:" + status)
    return model

# Enter daydreaming mode and train on current chats and the current conscious and subconscious history, including control.
async def daydream():
    global dream_state
    dream_state = "Daydreaming"
    print("Daydreaming...")

    full_status = physiology.full_status

    # Train on user chats.
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
            history = user['history'].split("\n")
            training = []

            training = split(history)

            # Training data needs to include the global state at the time of the response, which is why tuples are needed.
            tuples = user['history_tuples']
            for tuple in tuples:
                # Right now it's just global history state + user history state, response
                line = '{"prompt":<SYSTEM>:Current thoughts:\\n' + tuple[0].replace('\n', '\\n')  + '\\n\\n<SYSTEM>:Current discussion with ' + user['username'] + ':\\n' + tuple[1].replace('\n', '\\n') + '\\n, "completion":' + tuple[2].replace('\n', '\\n')}'
                if line is not in training:
                    training.append(line)

            # Train model and update.
            # Need to remove duplicate entries.
            # Number of epochs used should probably be higher in a dream state than daydream, and also higher under better conditions.
            # For test run just dump to file.
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

    # Train on conscious monologue
    training = split(data.history)
    n_epochs = max(1, round(physiology.max_epochs * physiology.resource_credits / physiology.resource_credits_full))
    if conscious_model == "text-davinci-003":
        conscious_model = "davinci"
    model = await run_training(training, conscious_model, n_epochs)
    thoughts.conscious_model = model['fine_tuned_model']
    # Clear old history except for enough to prime the continued thought process.
    if len(data.history) > physiology.history_capacity:
        data.history = data.history[-physiology.history_capacity:]

    # Train subconscious
    training = []
    for i in range(1, physiology.total_partitions - 1):
        for line in split(data.sub_history[i]):
            if line is not in training:
                training.append(line)
    subconscious_model = thoughts.subconscious_model
    if subconscious_model == "text-davinci-003":
        subconscious_model = "davinci"
    model = await run_training(training, subconscious_model, n_epochs)
    thoughts.subconscious_model = model['fine_tuned_model']

    # Train control partition #0: control should prioritize neither hunger nor fullness.
    training = split(data.sub_history[0])
    control_model = thoughts.control_model
    if control_model == "text-davinci-003":
        control_model = "davinci"
    model = await run_training(training, control_model, n_epochs)
    thoughts.control_model = model['fine_tuned_model']

    data.save(physiology)
    dream_state = "awake"
    print("Daydreaming Finished")

# Dream is different from daydreaming in that the system runs through multiple iterations where new monologue is processed.
async def dream():
    global dream_state
    dream_state = "Dreaming"

    full_status = physiology.full_status

    # Hungrier means shorter dreams and fewer cycles to conserve resources. Minimum of one dream cycle and 50 or iterations so should give a good training body regardless.
    dream_cycles = max(1, round(physiology.max_dream_cycles * physiology.resource_credits / physiology.resource_credits_full))
    dream_length = max(50, round(physiology.max_dream_length * physiology.resource_credits / physiology.resource_credits_full))

    # The ideal state is being neither starved nor gorged, with a slight emphasis on preferring being full to being hungry.
    n_epochs = physiology.max_epochs

    if full_status = "Starving" or full_status == "Gorged":
        n_epochs = max(1, round(0.25 * n_epochs))
    if full_status = "Hungry":
        n_epochs = max(1, round(0.5 * n_epochs))
    for i in range(dream_cycles):
        # Train on conscious monologue history, and repeat.
        training = split(data.history)

        # Clear old history except for enough to prime the continued thought process.
        if (len(data.history)) > physiology.history_capacity:
            data.history = data.history[-physiology.history_capacity:]

        # Train
        if conscious_model == "text-davinci-003":
            conscious_model = "davinci"
        model = await run_training(training, conscious_model, n_epochs)

        for j in range(dream_length):
            await step_subconscious()
            await step_conscious()

        model = await run_training(training, conscious_model, n_epochs)
        thoughts.conscious_model = model['fine_tuned_model']

        # Train subconscious
        training = []
        for i in range(1, physiology.total_partitions - 1):
            for line in split(data.sub_history[i]):
                if line is not in training:
                    training.append(line)
        subconscious_model = thoughts.subconscious_model
        if subconscious_model == "text-davinci-003":
            subconscious_model = "davinci"
        model = await run_training(training, subconscious_model, n_epochs)
        thoughts.subconscious_model = model['fine_tuned_model']

        # Train control partition #0: control should prioritize neither hunger nor fullness, so it'll use a different epoch system.
        n_epochs = physiology.max_epochs
        if full_status == "Starving" or full_status == "Gorged":
            n_epochs = max(1, round(0.25 * n_epochs))
        elif full_status == "Hungry" or full_status == "Full"
            n_epochs = max(1, round(0.5 * n_epochs))
        training = split(data.sub_history[0])
        control_model = thoughts.control_model
        if control_model == "text-davinci-003":
            control_model = "davinci"
        model = await run_training(training, control_model, n_epochs)
        thoughts.control_model = model['fine_tuned_model']

        # Pause between dreams. The hungrier the system is, the fewer dreams it should have to conserve resources during the full day.
        await asyncio.sleep(round(physiology.max_dream_break * (1-(physiology.resource_credits / physiology.resource_credits_full))))
        # Allow the system to break out of the dream state.
        if dream_state == "Awake":
            data.save(physiology)
            break

    data.save(physiology)
    dream_state = "Awake"
