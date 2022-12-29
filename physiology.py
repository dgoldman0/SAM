# SAM doesn't really have a physiology other than how many credits it has for tokens, etc. But that will do. This module will allow tracking of usage stats, once openai adds the API features to do so, or another workaround is found, such as authenticating and pulling from the web indirectly.

import thoughts
from datetime import datetime, timezone

# Control over physiology will occur on the subconscious level.

# Default values for openai
conscious_defaults = {"awake_temp": 0.5, "awake_top_p": 1, "sleep_temp": 1, "sleep_top_p": 1}
# Need to revise
subconscious_defaults = {"awake_temp": 0.9, "awake_top_p": 1, "sleep_temp": 1, "sleep_top_p": 1}

# Start slow for testing.
awake_think_period = 3
max_think_period = 4
min_think_period = 2

sleep_think_period = 0.5

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

# The number of resource credits currently available.
resource_credits = resource_credits_full / 2

# Until the dream system is implemented, this is always true.
awake = True

# Excite and depress physiology.
def excite():
    global think_period, min_think_period
    think_period = 0.5 * (think_period + min_think_period)

def depress():
    global think_period, max_think_period
    think_period = 0.5 * (think_period + max_think_period)

def stabilize():
    global think_period, awake_think_period, sleep_think_period
    if awake:
        think_period = 0.5 * (think_period + awake_think_period)
    else:
        think_period = 0.5 * (think_period + sleep_think_period)

# Review physiology and push any notifications necessary.
def review():
    global resource_credits, resource_credits_full, think_period, max_think_period, min_think_period, awake_think_period, sleep_think_period, full_status, awake
    print(datetime.now(timezone.utc).strftime("%H:%M:%S") + ": " + str(resource_credits) + " w/ think period of " + str(think_period))
    if resource_credits < 0.25 * resource_credits_full:
        depress()
        if resource_credits < 0.125 * resource_credits_full:
            thoughts.push_system_message("Starving", True)
            full_status = "Starving"
            return
        thoughts.push_system_message("Hungry", True)
        full_status = "Hungry"
        return

    # Having too many credits is less important than having too few, so notifications here should be more limited.
    if resource_credits > 0.75 * resource_credits_full:
        excite()
        if resource_credits > 0.875 * resource_credits_full:
            thoughts.push_system_message("Gorged", True)
            full_status = "Gorged"
            return
        if full_status != "Full":
            thoughts.push_system_message("Full", True)
            full_status = "Full"
        return
    full_status = ""
    stabilize()
