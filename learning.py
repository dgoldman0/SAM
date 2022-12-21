import globals
import server
import time
import thoughts

# Sleep will go through multiple phases of "dreaming" to generate a training set followed by actual training. It's hard to guess how much sleep will actually be needed to properly integrate new knowledge. Testing is the only way to really figure this out.

# Interrupt the sleep cycle: used when there's some important external stimulus, etc.

async def interrupt_sleep():
    return

# Take a snapshot of current thoughts and use it as training for the model.
async def integrate_thoughts(daydreaming):
    lock = globals.lock
    lock.acquire()
    history_snapshot = globals.history
    sub_snapshot = globals.sub_history.copy()
    lock.release()

    # Generate a training set by creating prompts from segments of the history with the completion being the next on the list in the history. Do this for both conscious and subconscious partitions if dreaming, and just a small fraction of conscious for daydreaming.

    lines = history_snapshot.split("\n")

    # Might be necessary to clean each line, but hopefully not.

    # Right now these are fixed parameters but depending on physiology they should be allowed to change a bit.
    clip_length = 10
    increment = 5
    if daydreaming:
        clip_length = 5
        increment = 4
    current = 0
    examples = []
    while current + clip_length + 1 < len(lines)
        prompt = "\n".join(lines[current:current + clip_length])
        completion = lines[current + clip_length + 1] + "\n"
        examples.append({"prompt": prompt, "completion"})

    # Integrate by fine-tuning using created training set.

    return

# Close active connections. The think and sub_think loops will continue to run.
async def dream():
    lock = globals.lock
    print("Entering dream state.")
    await server.stop_listening("sleep")

    # Change physiology for dream state.
    lock.acquire()
    physiology.sleep_temp = physiology.sleep_defaults["awake_temp"]
    physiology.sleep_top_p = physiology.sleep_defaults["awake_top_p"]
    physiology.think_period = physiology.sleep_think_period
    physiology.subthink_period = physiology.sleep_subthink_period
    lock.release()

    # Dreaming will cycle through periods of inner dialog and processing of results.
    start_time = time.time()

    # Dreaming will continue for 21600 seconds or 6 hours. The amount of sleep should really vary by a number of factors, including what's on SAM's mind.
    while time.time() - start_time < 21600:
        # Let 15 minutes of thinking pass by (essentially the REM sleep part)
        time.sleep(900)
        integrate_thoughts(false)

    # Dreaming has finished so it's time to wake up.
    lock.acquire()
    physiology.conscious_temp = physiology.conscious_defaults["awake_temp"]
    physiology.conscious_top_p = physiology.conscious_defaults["awake_top_p"]
    physiology.think_period = physiology.awake_think_period
    physiology.subthink_period = physiology.awake_subthink_period
    lock.release()

    await server.listen()

# Handle daydreaming. This function will be entered into when SAM has been spending a lot of time not paying attention, or hasn't received a lot of user input.
async def daydream():
    lock = globals.lock
    print("Daydreaming")

    lock.acquire()
    # Should be no active user anyway, since it makes sense to daydream while SAM is not paying attention already.
    thoughts.active_user = ""
    physiology.sleep_temp = physiology.sleep_defaults["awake_temp"]
    physiology.sleep_top_p = physiology.sleep_defaults["awake_top_p"]
    physiology.think_period = physiology.sleep_think_period
    physiology.subthink_period = physiology.sleep_subthink_period
    lock.release()

    # Daydream for a minute and integrate dream thoughts.
    time.sleep(60)
    await integrate_thoughts(true)

    lock.acquire()
    physiology.conscious_temp = physiology.conscious_defaults["awake_temp"]
    physiology.conscious_top_p = physiology.conscious_defaults["awake_top_p"]
    physiology.think_period = physiology.awake_think_period
    physiology.subthink_period = physiology.awake_subthink_period
    lock.release()
