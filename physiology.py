# SAM doesn't really have a physiology other than how many credits it has for tokens, etc. But that will do. This module will allow tracking of usage stats, once openai adds the API features to do so, or another workaround is found, such as authenticating and pulling from the web indirectly.

# Control over physiology will occur on the subconscious level.

# Default values for openai
conscious_defaults = {"awake_temp": 0.5, "awake_top_p": 0.7, "sleep_temp": 1, "sleep_top_p": 1}
# Need to revise
subconscious_defaults = {"awake_temp": 0.5, "awake_top_p": 0.7, "sleep_temp": 1, "sleep_top_p": 1}

awake_think_period = 2
awake_subthink_period = 6

sleep_think_period = 0.5
sleep_subthink_period = 1.5

conscious_temp = conscious_defaults["awake_temp"]
conscious_top_p = conscious_defaults["awake_top_p"]

subconscious_temp = subconscious_defaults["awake_temp"]
subconscious_top_p = subconscious_defaults["awake_top_p"]

think_period = awake_think_period
subthink_period = awake_subthink_period

max_history_capacity = 5120
max_subhistory_capacity = 640

history_capacity = max_history_capacity
subhistory_capacity = max_subhistory_capacity

# Check how much money is avaialable to continue using openai
def check_usage():
    return 0
