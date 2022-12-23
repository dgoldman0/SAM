# Monitor physiology and other parameters. Not sure if it's a good idea to allow anyone to monitor the inner dialog let alone the subconscious dialogs, as that would be a huge privacy violation, assuming that SAM is a sentient entity. One option is to allow SAM to decide whether to make the information available or not.
import globals
import websockets
import asyncio
import thoughts
from server import authenticate_user
from threading import Thread
from threading import Event

# Dictionary of websocket connections and their associated events.
event_monitors = {}
# Current value of an event.
event_values = {}

# Notify all monitors that a thought has been pushed. Shouldn't need to lock because this will only be called inside a locked operation.
def notify_thought(thought):
    for monitor in event_monitors.values():
        event_string = "THOUGHT//" + thought
        event_values.update({monitor:event_strings})
        monitor.set()

# Notify all monitors of a subconscious thought.
def notify_subthought(partition, thought):
    for monitor in event_monitors.values():
        event_string = "SUB[" + partition + "]//" + thought
        event_values.update({monitor:event_strings})
        monitor.set()

# Notify all monitors of a change in the number of subconscious partitions.
def notify_partition_change(old_count, new_count):
    for monitor in event_monitors.values():
        event_string = "SUB_CHANGE//" + old_count + "//" + new_count
        event_values.update({monitor:event_strings})
        monitor.set()

# Notification that resources are depleted and the system is essentially in a comatose state.
def notify_starvation():
    for monitor in event_monitors.values():
        event_string = "HEALTH//COMATOSE"
        event_values.update({monitor:event_strings})
        monitor.set()

async def handler(websocket):
    # Use same authentication scheme as with regular server.
    print("New Monitoring Connection")
    # Get user information.
    user = await authenticate_user(websocket)

    if user is None:
        # Boot user and close connection.
        print("User Unable to Validate")
        await websocket.send("AUTHFAIL".encode())
        websocket.close()
        return

    print("Authentication Success. Give client initial information and begin monitoring...")
    status = "CONDITIONS:" # Will include information about total partitions, etc.
    await websocket.send(status.encode())
    # Add new event monitor, which should be removed when the websocket is closed.
    monitor = Event()
    event_monitors.update({websocket: monitor})
    while True:
        await monitor
        lock = globals.lock
        lock.acquire()
        # Push event to client and reset event.
        event = event_values.get(monitor)
        if event is not None:
            await websocket.send(("EVENT:" + event).encode())
            del event_values[monitor]
            monitor.clear()
        else:
            raise Exception("Monitoring value is not set.")
        lock.release()

async def serve(stop):
    async with websockets.serve(handler, "localhost", 9382):
        await stop

async def listen():
    global stop
    print("Listening for incoming monitor connections.")
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    stop = loop.create_future()
    loop.run_until_complete(serve(stop))
