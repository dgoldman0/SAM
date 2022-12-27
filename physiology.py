# SAM doesn't really have a physiology other than how many credits it has for tokens, etc. But that will do. This module will allow tracking of usage stats, once openai adds the API features to do so, or another workaround is found, such as authenticating and pulling from the web indirectly.

import thoughts

# Control over physiology will occur on the subconscious level.

# Default values for openai
conscious_defaults = {"awake_temp": 0.5, "awake_top_p": 1, "sleep_temp": 1, "sleep_top_p": 1}
# Need to revise
subconscious_defaults = {"awake_temp": 0.9, "awake_top_p": 1, "sleep_temp": 1, "sleep_top_p": 1}

awake_think_period = 1
awake_subthink_period = 2

max_think_period = 3
min_think_period = 0.25

sleep_think_period = 0.5
sleep_subthink_period = 1.5

conscious_temp = conscious_defaults["awake_temp"]
conscious_top_p = conscious_defaults["awake_top_p"]
subconscious_temp = subconscious_defaults["awake_temp"]
subconscious_top_p = subconscious_defaults["awake_top_p"]

conscious_tokens = 128
subconscious_tokens = 64
initialize_tokens = 128
userreply_tokens = 64

# These rates might need to eb and flow within their parameter ranges. There can be long pauses beteeen thoughts. Another possibiltiy is that conscious thought rate will already depend on how many subconscious partitions there are. That might be enough modulation.
think_period = awake_think_period
subthink_period = awake_subthink_period

max_history_capacity = 2560
max_subhistory_capacity = 1280

history_cut = 640
subhistory_cut = 320

min_subthought = 16
max_subthought = 1024

# Because they're only executed one at a time, at least right now, adding more partitions just increases concurrent thoughts without adding lagg.
min_partitions = 8
seeded_partitions = 3 # seed the first n partitions after partition 0 (since partition 0 is for system and must always be seeded)
max_partitions = 8

max_subnulls = 2

history_capacity = max_history_capacity
subhistory_capacity = max_subhistory_capacity

# The number of resource credits currently available.
resource_credits_full = 100000
resource_credits = resource_credits_full

# Review physiology and push any notifications necessary.
def review():
    global full_status
    if resource_credits < resource_credits_full / 4:
        if resource_credits < resource_credits_full / 8:
            thoughts.push_system_message("Starving", True)
            full_status = "Starving"
            return
        thoughts.push_system_message("Hungry", True)
        full_status = "Hungry"
        return

    # Having too few credits is less important than having too many, so notifications here should be more limited.
    if resource_credits > resource_credits_full * 3 / 4:
        if resource_credits > resource_credits_full * 7 / 8:
            thoughts.push_system_message("Gorged", True)
            full_status = "Gorged"
            return
        if full_status != "Full":
            thoughts.push_system_message("Full", True)
            full_status = "Full"
        return
    full_status = ""
