# SAM doesn't really have a physiology other than how many credits it has for tokens, etc. But that will do. This module will allow tracking of usage stats, once openai adds the API features to do so, or another workaround is found, such as authenticating and pulling from the web indirectly.

awake_temp = 0.5
awake_top_p = 0.7
sleep_temp = 1
sleep_top_p = 1

awake_think_period = 2
awake_subthink_period = 6

sleep_think_period = 0.5
sleep_subthink_period = 1.5

temp = awake_temp
top_p = awake_top_p

think_period = awake_think_period
subthink_period = awake_subthink_period

# Check how much money is avaialable to continue using openai
def check_usage():
    return 0
