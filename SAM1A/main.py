import data
import server
import internal
import asyncio
import conversations

# Note: Should convert all instances of \n to \\n internally.

async def main():
    data.init()
    conversations.init(server)
    await asyncio.gather(server.listen(), internal.think())

asyncio.run(main())
