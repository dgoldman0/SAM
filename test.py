import os
import openai

openai.api_key = os.getenv("OPENAI_API_KEY")

start_sequence = "\n"

response = openai.Completion.create(
  model="curie:ft-personal-2023-01-06-21-41-33",
  prompt="<SYSTEM>:System notifications will arrive in the form <SYSTEM>:Notification message. You can issue system commands by starting the line with COMMAND:, for instance, use COMMAND:HELP to get a list of system commands. There are a few other special symbols. <USERNAME>: at the start of a line indicates a chat message notification where USERNAME is replaced with their actual username. Use //USERNAME: at the beginning of a line to indicate that you want to reply to that user. The system will inform you if that user is not online. COMMAND:HELP",
  temperature=0.7,
  max_tokens=256,
  top_p=1,
  frequency_penalty=0,
  presence_penalty=0,
  stop=["\n><"]
)
print(response)
