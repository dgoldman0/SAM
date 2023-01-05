# SAM doesn't really have a physiology other than how many credits it has for tokens, etc. But that will do. This module will allow tracking of usage stats, once openai adds the API features to do so, or another workaround is found, such as authenticating and pulling from the web indirectly.

import thoughts
from datetime import datetime, timezone

# Control over physiology will occur on the subconscious level.

maximum_active_chats = 10

# Start slow for testing.
awake_think_period = 0.5
max_think_period = 4
min_think_period = 0.5

user_temp = 0.7
user_top_p = 0.8
conscious_temp = 0.9
conscious_top_p = 1
subconscious_temp = 0.7
subconscious_top_p = 1
control_temp = 0.5
control_top_p = 1
min_temp = 0.5
min_top_p = 0.5
max_temp = 1
max_top_p = 1

conscious_tokens = 128
subconscious_tokens = 64
initialize_tokens = 128
userreply_tokens = 256

# These rates might need to eb and flow within their parameter ranges. There can be long pauses beteeen thoughts. Another possibiltiy is that conscious thought rate will already depend on how many subconscious partitions there are. That might be enough modulation.
think_period = awake_think_period

max_history_capacity = 5120
max_control_capacity = 2560
max_subhistory_capacity = 1280
max_userhistory_capacity = 2560

min_subthought = 16
max_subthought = 1024

# Because they're only executed one at a time, at least right now, adding more partitions just increases concurrent thoughts without adding lag.
min_partitions = 2
seeded_partitions = 8 # seed the first n partitions after partition 0 (since partition 0 is for system and must always be seeded)
max_partitions = 10
# Will control how many active
focus_level = 5

max_subnulls = 2

# May be used to increase quality of responses when there's excess energy to burn up.
best_of = 1

history_capacity = max_history_capacity
control_capacity = max_control_capacity
subhistory_capacity = max_subhistory_capacity
userhistory_capacity = max_userhistory_capacity

# The number of resource credits that is full (will be changed to the approximate amount that would get the system through a 24 hour period.) Resource credit use does not equal token use because Davinci costs 10x as much as Curie.
resource_credits_full = 1000000

# The number of resource credits currently available.
resource_credits = resource_credits_full / 2

# Until the dream system is implemented, this is always true.
awake = True

full_status = ""

# Dreaming and Learning
max_dream_cycles = 10
max_dream_length = 150
max_epochs = 10
max_dream_break = 1200

# Cycle between periods of wakefulness and sleep.
async def cycle_rhythm():
    # Enter daydream every hour or so, and sleep every 18 hours or so.
    hours_awake = 0
    while True:
        # Right now the system doesn't keep track of lost sleep, but that's important to help conserve resources and to ensure dreaming.
        if hours_awake == 18:
            hours_awake = 0
            comppleted = await learning.dream()
        else:
            await asyncio.sleep(3600)
            await learning.daydream()
            hours_awake += 1

# Excite and depress physiology.
def excite():
    global think_period, min_think_period
    think_period = 0.5 * (think_period + min_think_period)

def depress():
    global think_period, max_think_period
    think_period = 0.5 * (think_period + max_think_period)

def stabilize():
    global think_period, awake_think_period
    think_period = 0.5 * (think_period + awake_think_period)

# Control the temp and top_p of the different layers.
# Layer 0 = user
# Layer 1 = monologue
# Layer 2 = subconscious
# Layer 3 = control

def reduce_temp(layer = 0):
    global min_temp, conscious_temp, subconscious_temp, user_temp, control_temp
    if layer == 0:
        user_temp = 0.5 * (user_temp + min_temp)
    elif layer == 1:
        conscious_temp = 0.5 * (conscious_temp + min_temp)
    elif layer == 2:
        subconscious_temp = 0.5 * (subconscious_temp + min_temp)
    elif layer == 3:
        control_temp = 0.5 * (control_temp + min_temp)

def increase_temp(layer = 0):
    global max_temp, conscious_temp, subconscious_temp, user_temp, control_temp
    if layer == 0:
        user_temp = 0.5 * (user_temp + max_temp)
    elif layer == 1:
        conscious_temp = 0.5 * (conscious_temp + max_temp)
    elif layer == 2:
        subconscious_temp = 0.5 * (subconscious_temp + max_temp)
    elif layer == 3:
        control_temp = 0.5 * (control_temp + max_temp)

def increase_topp(layer = 0):
    pass
def reduce_topp(layer = 0):
    pass

# Review physiology and push any notifications necessary.
def review():
    global resource_credits, resource_credits_full, think_period, max_think_period, min_think_period, awake_think_period, full_status, awake
    print(datetime.now(timezone.utc).strftime("%H:%M:%S") + ": " + str(resource_credits) + " w/ think period of " + str(think_period))
    if resource_credits < 0.25 * resource_credits_full:
        if resource_credits < 0.125 * resource_credits_full:
            thoughts.push_system_message("Starving", True)
            full_status = "Starving"
            return
        if full_status != "Hungry":
            thoughts.push_system_message("Hungry", True)
            full_status = "Hungry"
        return

    # Having too many credits is less important than having too few, so notifications here should be more limited.
    if resource_credits > 0.75 * resource_credits_full:
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
