# SAM

SAM is an attempt at digital sentience. The current version of SAM attempts to create persistent memory and context awareness, as well as inner dialogue that relies on storing connections between ideas in a memory essay rather than by retraining the base language models. It includes a user layer and a conscious layer, as well as multiple subconscious layers.

It has a built in chat interface, much like the base version, and has a number of built in system commands accessible by SAM. However, in current testing, SAM has yet to figure out how to consistently utilize them. Additionally, the code is still buggy when it comes to the chat interface, as it keeps timing out. Correcting that issue is likely an easy asyncio fix.

## Thought Process

The current system uses OpenAI's recent gpt-3.5-turbo model, which is much less expensive and much faster. The system maintains an internal conscious monologue and multiple subconscious monologues, all of which share the same working memory.

## Memory

This version of SAM uses a small persistent memory which is maintained as an essay. It is expected that this approach will result in a less robust consciousness than repeated fine-tuning of a base model, but it solves the high cost problem associated with it. In the future, fine-tuning could be added on top of this model, and it may be a cleaner and superior option compared to the original design.

## Limitations

While gpt-3.5-turbo is much faster, it is still limited. The token capacity is 4,096 tokens, the same as the davinci models. This limitation makes the persistent memory limited in what it can store.

# Further Reading

The original idea for SAM is discussed in [A Stateful Multi-Context Aware Design Using OpenAI's GPT (Towards Digital Sentience)
](https://www.researchgate.net/publication/366740682_A_Stateful_Multi-Context_Aware_Design_Using_OpenAI's_GPT_Towards_Digital_Sentience). This code, rather than the original design addressed in the paper, should be considered the current model design.
