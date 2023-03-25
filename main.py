import data
import server
import internal
import asyncio
import conversations

# Note: Should convert all instances of \n to \\n internally.

async def main():
    data.init()
    conversations.init(server)
    channels = data.getChannelList()
    think_tasks = []
    subthink_tasks = []
    for channel in channels:
        think = asyncio.create_task(internal.think(channel))
        subthink = asyncio.create_task(internal.subthink(channel))
        think_tasks.append(think)
        subthink_tasks.append(subthink)
    await asyncio.gather(server.listen(), *think_tasks, *subthink_tasks)
        
asyncio.run(main())
