# Give preference to training sets that yield more credits, when the system is hungry, but don't when it isn't.
# When we train an AI, we train it on our decisions. This system trains itself on its own decisions AND our decisions.
# Drop blank histories. Rank by amount paid / line generated, so a short conversation which brings in a lot is really good.

import server

from random import randint

# Number of epochs used should probably be higher in a dream state than daydream, and also higher under better conditions.
async def daydream():
    # Need to figure out how to temporarily halt server connections
    for user in server.user_connections.items():
        tips = user['tips']
        spent = user['tokens_spent']
        if spent > 0:
            efficiency = tips / spent
            history = user['history'].split("\n")
            cur = 0
            training = ""
            while cur < len(history) - 2:
                # Create prompts between 3 and 8 lines long.
                prompt = []
                completion = []
                prompt_size = randint(3,8)
                completion_size = randint(3, 8)
                if len(history) > cur + prompt_size + completion_size:
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
    #            training += '{"prompt":' + tuple[0]  + '\\n, "completion":' + tuple[]}'
