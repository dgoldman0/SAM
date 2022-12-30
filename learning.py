# Give preference to training sets that yield more credits, when the system is hungry, but don't when it isn't.
# When we train an AI, we train it on our decisions. This system trains itself on its own decisions AND our decisions.
# Drop blank histories. Rank by amount paid / line generated, so a short conversation which brings in a lot is really good.

import server
import data
import thoughts
from random import randint
import asyncio
import io
import openai
import uuid

daydreaming = False
dreaming = False

# Create prompts and completions by randomly breaking up the history into chunks between 1 and 5 lines long, multiple times. Right now 3, but will change based on a number of factors.
def split(text, iterations = 5):
    training = []
    for in in range(iterations):
        cur = 0
        while cur < len(text) - 2:
            prompt = []
            completion = []
            prompt_size = randint(1,5)
            completion_size = randint(1, 5)
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

async def daydream():
    global daydreaming
    daydreaming = True
    print("Daydreaming...")

    users = []
    # Prioritize high tipping when starving, hungry, or neutral. Don't prioritize if full or gorged.
    prioritize = False
    if physiology.full_status != "Gorged" and physiology.full_status != "Full":
        prioritize = True # Will cause the number of epochs used in training to decrease with lower efficiency, and reduce epochs for general training.
        users = server.user_connections.items().sort(reverse=True, key=efficiency)
    for user in users:
        history = user['history'].split("\n")
        training = []
        # Require minimum of 50 lines of chat.
        if len(history > 50):
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
            n_epochs = physiology.max_epochs
            if physiology.full_status == "Hungry":
                n_epochs = round(0.5 * n_epochs)
            elif physiology.full_status == "Starving":
                n_epochs = round(0.25 * n_epochs)
            model = await run_training(training, thoughts.user_model, n_epochs)
            thoughts.user_model = model['fine_tuned_model']
        # Reset history and tip data.
        if (len(user['history'])) > physiology.userhistory_capacity:
            user['history'] = user['history'][-physiology.userhistory_capacity:]
        user['history_tuples'] = []
        user['tips'] = 0
        user['tokens_spent'] = 0

    # Train on conscious monologue history.
    training = split(data.history)
    n_epochs = physiology.max_epochs
    model = await run_training(training, thoughts.conscious_model, n_epochs)

    # Clear old history except for enough to prime the continued thought process.
    if (len(data.history)) > physiology.history_capacity:
        data.history = data.history[-physiology.history_capacity:]

    daydreaming = False
    print("Daydreaming Finished")

# The ideal state is being neither hungry or full, neutral will get the most training epochs.
# Dream is different from daydreaming in that the system runs through multiple iterations where new monologue is processed.
async def dream():
    # Not even close to working, and doesn't deal with training subconscious layers. The exact number of iterations (how many dreams) and length of each dream, will be variable based on physiology, etc.
    for i in range(physiology.max_dream_cycles):
        # Train on conscious monologue history, and repeat.
        training = split(data.history)

        # Train

        # Clear old history except for enough to prime the continued thought process.
        if (len(data.history)) > physiology.history_capacity:
            data.history = data.history[-physiology.history_capacity:]

        for j in range(physiology.max_dream_length):
            await step_subconscious()
            await step_conscious()

        await run_training()
        # Pause between dreams.
        await asyncio.sleep(100)
