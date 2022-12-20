# Global variables

# Final version will have different models for conscious dialog and subconscious partitions.
#conscious = "davinci:ft-personal-2022-12-14-17-05-26" # includes both general knoweldge and concept connections
# Eventually each subconscious partition might run on a different model.
#subconscious = "davinci:ft-personal-2022-12-14-17-05-26" # includes both general knoweldge and concept connections

# Good to test code with the super cheap basic models, at least to check for errors.
conscious = "davinci"
subconscious = "davinci"

# Full history of all thinking
full_history = ""

# The history between active user and Sam, as well as the direct inner dialog.
history = ""

# History between inner voice and subconscious, to be replaced with an array of histories.
sub_history = []

lock = Lock()
