# Give preference to training sets that yield more credits, when the system is hungry, but don't when it isn't.
# When we train an AI, we train it on our decisions. This system trains itself on its own decisions AND our decisions.
# Drop blank histories. Rank by amount paid / line generated, so a short conversation which brings in a lot is really good.

import server

from random import randint

daydreaming = False
dreaming = False

async def daydream():
    global daydreaming
    daydreaming = True
    print("Daydreaming...")
    for user in server.user_connections.items():
        tips = user['tips']
        spent = user['tokens_spent']
        print("Spent: " + str(spent))
        if True:
#        if spent > 0:
            efficiency = tips / spent
            history = user['history'].split("\n")
            # Require minimum of 20 lines of chat.
            if len(history > 20):
                training = ""
                # Create prompts and completions by randomly breaking up the history into chunks between 1 and 10 lines long, multiple times. Right now 3, but will change based on a number of factors.
                for in in range(5):
                    cur = 0
                    while cur < len(history) - 2:
                        prompt = []
                        completion = []
                        prompt_size = randint(1,10)
                        completion_size = randint(1, 10)
                        if len(history) > cur + prompt_size + completion_size:
                            prompt = history[cur:cur + prompt_size]
                            completion = history[cur + prompt_size:cur + prompt_size + completion_size]
                            cur += (prompt_size + completion_size)
                        else:
                            prompt = history[cur:-1]
                            completion = history[-1]
                            cur = len(history)
                        if training != "":
                            training += "\n"
                        training += '{"prompt":' + "\\n".join(prompt) + '\\n, "completion":' '\\n'.join(completion) + "\\n}"]

                # Training data needs to include the global state at the time of the response, which is why tuples are needed.
                tuples = user['history_tuples']
                for tuple in tuples:
                    if training != "":
                        training += "\n"
                    # Right now it's just global history state + user history state, response
                    training += '{"prompt":Current thoughts:\\n' + tuple[0].replace('\n', '\\n')  + '\\n\\nCurrent discussion with ' + user['username'] + ':\\n' + tuple[1].replace('\n', '\\n') + '\\n, "completion":' + tuple[2].replace('\n', '\\n')}'

    # Train model and update.
    # For test run just dump to file.
    f = open("training.txt", "w")
    print("Training file size: " + str(len(training)))
    f.write(training)
    f.close()
    # Number of epochs used should probably be higher in a dream state than daydream, and also higher under better conditions.
    daydreaming = False
    print("Daydreaming Finished")

async def dream():
