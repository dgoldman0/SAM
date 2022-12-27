# Learning System

It's still difficult to figure out exactly what training data to create. There are many different approaches, some of which might work much better than others.

## Physiology

Resource Credits

## Training Data

When we train an AI, we train it on our decisions. This system trains itself on its own decisions AND our decisions.

Because the system relies on resource credits, one option is to give preference to conversations that yield more credits. Additionally, the selection of training can depend on how full or hungry the system feels. Essentially, the ideal training is when the system is satisfied. Therefore, preferential treatment would only be given when there is need for it.

Option: If the system is hungry, give preference to discussions that yield more credits. If the system is full, give preference to discussions that yield fewer credits. If the system is neither hungry nor full, don't give preference.

### Dreaming

The easiest option for training the user chat model is to use a triple of (monologue, user history, response) and create prompts of monologue + \n + user history with completion as the response. It shouldn't be a problem that the monologue ad user history aren't interspersed, since the training system should be able to guess pretty well on the mapping between them.

The conscious monologue can simply be broken up into random size chunks. As for how much of the monologue to use, daydreaming will just train on the current globals.history, while dreaming will train on the entire monologue history for the entire day. Furthermore, to fully dream, after the full day history training, the system will cycle through turning the monologue back on, letting it run until it's generated max_history_capacity more monologue, training, and repeating.

Dreaming is expensive but can be used to save money, by not training, and only leaving the subconscious active, and at a reduced rate to check for things that could wake it up. The amount of time spent between dreams should decline with more resource credit availability. Basically, low resource credits will make the system sleep more so it conserves credits. Figuring out how long the system should sleep for is going to be difficult. 
