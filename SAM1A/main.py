import data
import server
import internal
import asyncio

async def main():
    await asyncio.gather(server.listen(), internal.think())

data.init()
asyncio.run(main())
