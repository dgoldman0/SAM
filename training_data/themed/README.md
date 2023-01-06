# Themed Training

The text-davinci-3 model is quite good at responding to users, and integrating the text-davinci-3 model into this system already produces fairly decent results, including while testing for short term memory storage and multi-context interaction. However, the text-davinci-3 model cannot be fine-tuned. There's been some discussion that it will be possible to fine-tune these models in the future, but for now, only base models and custom models can be fine-tuned.

Unfortunately, substituting the base model in for the text-davinci-3 model yields terrible results. It's simply not trained enough to output anything close to what is reasonable. So a lot of initial training is needed. There are a number of options available to train the base model. One option is to simply use a wide range of different texts and interactions. But fine-tuning can also be done on more personalized data.

The themed training system uses discussions, thought maps, and other material from the creator of this project, myself, thus imparting a segment of my thought process to the model. There is no real academic benefit of doing so, it is largely for personal interests that this method of fine-tuning has been chosen over other options.

## General Knowledge and Concept Connections

The first component of the training set is the general knowledge training set, which includes a number of questions or statements, and responses to those questions and statements, based on how I would answer them. The next segment of training is the concept connections, which basically is a simple thought web connecting various ideas together.

## Stream of Thoughts

To create a lot of material, I created a stream of thought essay, where each paragraph is largely self contained information, but the topic of one paragraph extends naturally from the previous topic. The document is then tokenized into chunks of prompts and completions of different lengths for training.

### Prompt-Completions From Stream

To further train the model and make it more responsive, each paragraph from the stream of thoughts essay is coupled with a number of prompt questions and statements that match the content of the paragraph. The training set also includes questions and statements that can be prompted by the statements made in each paragraph.

## Training for Format

One issue with the system is that it tends to output a lot of junk at the beginning of the completion, due to the special keycodes used by the system. Training includes both raw prompt and completions, and also prompts that are prepended with mockup information to help train away the tendency to copy these keycodes.
