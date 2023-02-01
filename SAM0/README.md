# SAM0

SAM0 is little more than a chatbot with a working associative memory. It's far more limited than what SAM will be, but it can still be useful to those interested in how rumination can restructure connections between ideas and how it is important for building an internal working understanding of the world.

Unlike SAM, which will have a constantly active internal monologue, SAM0 only has a monologue while it's in a dream sequence. The dream sequence is also manually controlled. Dream sequences occur as sets of m dreams of length n, controlled manually by altering the code in the loop.

## Commands

Commands start with a backslash. The current commands are as follows.

- memory: show current long term memory map.
- working: show current working memory for the current discussion
- dream: initiate a dream sequence
- save: save the current long term memory to file.

# Notes

- SAM0 is very susceptible to initial conversation bias, if starting from a blank memory map. However, the bias may reduce over time, as it has a chance to integrate a more diverse set of topics from future conversations.
- Because of the token limit of token limits for OpenAI models, the associative memory map is restricted to about 8,000 characters. Functionality may become more unpredictable once that limit has been reached.
