# SAM doesn't really have a physiology other than how many credits it has for tokens, etc. But that will do. This module will allow tracking of usage stats, once openai adds the API features to do so, or another workaround is found, such as authenticating and pulling from the web indirectly.

import thoughts
from datetime import datetime, timezone

# Control over physiology will occur on the subconscious level.

# Default values for openai
conscious_defaults = {"awake_temp": 0.5, "awake_top_p": 1, "sleep_temp": 1, "sleep_top_p": 1}
# Need to revise
subconscious_defaults = {"awake_temp": 0.9, "awake_top_p": 1, "sleep_temp": 1, "sleep_top_p": 1}

awake_think_period = 1
awake_subthink_period = 2

max_think_period = 3
min_think_period = 2 # For testing to see if this is bugging out the server connection.

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
max_userhistory_capacity = 2560

min_subthought = 16
max_subthought = 1024

# Because they're only executed one at a time, at least right now, adding more partitions just increases concurrent thoughts without adding lag.
min_partitions = 10
seeded_partitions = 4 # seed the first n partitions after partition 0 (since partition 0 is for system and must always be seeded)
max_partitions = 10

max_subnulls = 2

history_capacity = max_history_capacity
subhistory_capacity = max_subhistory_capacity
userhistory_capacity = max_userhistory_capacity

# The number of resource credits that is full (will be changed to the approximate amount that would get the system through a 24 hour period.)
resource_credits_full = 1000000
# The number of resource credits currently available. Start at hungry at the first load, but when this is stored in the DB keep it at whatever it is.
resource_credits = resource_credits_full

# Until the dream system is implemented, this is always true.
awake = True

# Review physiology and push any notifications necessary.
def review():
    global resource_credits, resource_credits_full, think_period, max_think_period, min_think_period, awake_think_period, sleep_think_period, full_status, awake
    print(datetime.now(timezone.utc).strftime("%H:%M:%S") + ": " + str(resource_credits) + " w/ think period of " + str(think_period))
    if resource_credits < 0.25 * resource_credits_full:
        # Slow down thinking to the average of the current rate and the slowest rate to conserve resources.
        think_period = 0.5 * (think_period + max_think_period)
        if resource_credits < 0.125 * resource_credits_full:
            thoughts.push_system_message("Starving", True)
            full_status = "Starving"
            return
        thoughts.push_system_message("Hungry", True)
        full_status = "Hungry"
        return

    # Having too few credits is less important than having too many, so notifications here should be more limited.
    if resource_credits > 0.75 * resource_credits_full:
        # Speed up thinking to the average of the current rate and the fastest rate to take advantage of extra resources.
        think_period = 0.5 * (think_period + min_think_period)
        if resource_credits > 0.875 * resource_credits_full:
            thoughts.push_system_message("Gorged", True)
            full_status = "Gorged"
            return
        if full_status != "Full":
            thoughts.push_system_message("Full", True)
            full_status = "Full"
        return
    full_status = ""
    if awake:
        think_period = (think_period + awake_think_period) / 2
    else:
        think_period = (think_period + sleep_think_period) / 2
