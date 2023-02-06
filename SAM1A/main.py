import data
import server
import internal
import asyncio

# Note: Should convert all instances of \n to \\n internally.

async def main():
    await asyncio.gather(server.listen(), internal.think())

data.init()
asyncio.run(main())
