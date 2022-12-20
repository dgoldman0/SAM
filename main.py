import globals
import thoughts
import sleep
import server
# Future version should start thinking about a new information integration function where new information is integrated. But that would require more training which is expensive.
# I have System Notifications. Now I need System Commands to get the AI to control things.

# Want to be able to include an offline history so the bot can talk to the users while they're offline. Though not what kind of code to get the bot to do that.

async def main():
    wake_ai()
    async with websockets.serve(converse, "localhost", 9381):
        await asyncio.Future()  # run forever

# Terminate system gracefully.
async def terminate():
    database.close()
    
asyncio.run(main())
