# Set for the 32K model
internal_capacity = 12500 # Random guess that 10% of the total subconscious capacity (5000 * 25) is reasonable.
conversation_capacity = 5000
subs = 25 # Number of subconscious cycles
contraction_tolerance = 0.85 # Maximum tolerable reduction in long term memory - more loss is tolerable with higher subs because they store some data
thinkpause = 1
subpause = 0.1
features = 'This individual has a lot in common, in terms of personality, with Uncle Iroh. He is wife and calm. He is caring and helpful. He speaks in eloquant and flowery language.'
# If true, will check for internal system commands and run them as part of the thought process.
run_commands_internally = False