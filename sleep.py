import globals
import server

# Sleep will go through multiple phases of "dreaming" to generate a training set followed by actual training. It's hard to guess how much sleep will actually be needed to properly integrate new knowledge. Testing is the only way to really figure this out.

# Interrupt the sleep cycle: used when there's some important external stimulus, etc.

async def interrupt_sleep():
    return

# Close active connections. The think and sub_think loops will continue to run.
async def dream():
    lock = globals.lock
    print("Entering dream state.")
    await server.stop_listening("sleep")

    # Change physiology for dream state.
    lock.acquire()
    physiology.temp = physiology.sleep_temp
    physiology.top_p = physiology.sleep_top_p
    physiology.think_period = physiology.sleep_think_period
    physiology.subthink_period = physiology.sleep_subthink_period
    lock.release()

    # Allow REM sleep
    # Dreaming has finished so it's time to wake up.
    lock.acquire()
    physiology.temp = physiology.awake_temp
    physiology.top_p = physiology.awake_top_p
    physiology.think_period = physiology.awake_think_period
    physiology.subthink_period = physiology.awake_subthink_period
    lock.release()
    lock.acquire()

    await thoughts.wake_ai()
    await server.listen()
