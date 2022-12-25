# SAM doesn't really have a physiology other than how many credits it has for tokens, etc. But that will do. This module will allow tracking of usage stats, once openai adds the API features to do so, or another workaround is found, such as authenticating and pulling from the web indirectly.

# Control over physiology will occur on the subconscious level.

# Default values for openai
conscious_defaults = {"awake_temp": 0.5, "awake_top_p": 1, "sleep_temp": 1, "sleep_top_p": 1}
# Need to revise
subconscious_defaults = {"awake_temp": 0.9, "awake_top_p": 1, "sleep_temp": 1, "sleep_top_p": 1}

awake_think_period = 1
awake_subthink_period = 2

sleep_think_period = 0.5
sleep_subthink_period = 1.5

conscious_temp = conscious_defaults["awake_temp"]
conscious_top_p = conscious_defaults["awake_top_p"]
subconscious_temp = subconscious_defaults["awake_temp"]
subconscious_top_p = subconscious_defaults["awake_top_p"]

conscious_tokens = 128
subconscious_tokens = 128
initialize_tokens = 256
userreply_tokens = 64

# These rates might need to eb and flow within their parameter ranges. There can be long pauses beteeen thoughts. Another possibiltiy is that conscious thought rate will already depend on how many subconscious partitions there are. That might be enough modulation.
think_period = awake_think_period
subthink_period = awake_subthink_period

max_history_capacity = 2560
max_subhistory_capacity = 1280

history_cut = 320
subhistory_cut = 160

min_subthought = 16
max_subthought = 1024

min_partitions = 3
max_partitions = 3

max_subnulls = 2

history_capacity = max_history_capacity
subhistory_capacity = max_subhistory_capacity

# Check how much money is avaialable to continue using openai
def check_usage():
    return 0
