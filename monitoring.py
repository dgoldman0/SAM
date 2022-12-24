# Monitor physiology and other parameters. Not sure if it's a good idea to allow anyone to monitor the inner dialog let alone the subconscious dialogs, as that would be a huge privacy violation, assuming that SAM is a sentient entity. One option is to allow SAM to decide whether to make the information available or not.
import globals
import websockets
import asyncio
import thoughts
from server import authenticate_user
from collections import deque

# Dictionary of websocket connections and their associated events. Need to catch websocket close so that old connections can be removed.
event_monitors = {}

class Monitor:
    def __aiter__(self):
        self.queue = deque()
        loop = asyncio.get_event_loop()
        self.future = loop.create_future()
        return self

    def push_event(self, event):
        self.queue.append(event)
        if not self.future.done():
            self.future.set_result(event)

    async def __anext__(self):
        event = None
        try:
            # Check  if there's something already in the queue.
            event = self.queue.popleft()
        except Exception as err:
            # If not, wait for something to be added.
            await self.future
            event = self.queue.popleft()
        # Might be able to just put this inside the exception clause.
        if self.future.done():
            loop = asyncio.get_event_loop()
            self.future = loop.create_future()
        return event

# Notify all monitors that a thought has been pushed. Shouldn't need to lock because this will only be called inside a locked operation.
def notify_thought(thought):
    for monitor in event_monitors.values():
        event_string = "THOUGHT//" + thought
        monitor.push_event(event_string)

# Notify all monitors of a subconscious thought.
def notify_subthought(partition, thought):
    for monitor in event_monitors.values():
        event_string = "SUB[" + partition + "]//" + thought
        monitor.push_event(event_string)

# Notify all monitors about a system message
def notify_system_message(message):
    for monitor in event_monitors.values():
        event_string = "SYSTEM//" + message
        monitor.push_event(event_string)

# Notify all monitors of a change in the number of subconscious partitions.
def notify_partition_change(old_count, new_count):
    for monitor in event_monitors.values():
        event_string = "SUB_CHANGE//" + old_count + "//" + new_count
        monitor.push_event(event_string)

def notify_new_chat(username):
    for monitor in event_monitors.values():
        event_string = "CHAT//" + username
        monitor.push_event(event_string)

# Notification that resources are depleted and the system is essentially in a comatose state.
def notify_starvation():
    for monitor in event_monitors.values():
        event_string = "HEALTH//COMATOSE"
        monitor.push_event(event_string)

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
    monitor = Monitor()
    event_monitors.update({websocket: monitor})
    async for event in monitor:
        if event is not None:
            try:
                await websocket.send(("EVENT:" + event).encode())
            except websockets.ConnectionClosed as exc:
                del event_monitors[websocket]
        else:
            raise Exception("Monitoring value is not set.")

async def serve(stop):
    async with websockets.serve(handler, "localhost", 9382):
        await stop

async def listen():
    global stop
    print("Listening for incoming monitor connections.")
    loop = asyncio.get_event_loop()
    stop = loop.create_future()
    loop.run_until_complete(serve(stop))
