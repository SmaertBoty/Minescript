Eventlib is a library aiming to add new events, while keeping minescripts `EventQueue`. It is a drag n' drop library, meaning you just import it, and you already have everything set up.
Requires 5.0b11 or higher

As of now, it contains only 1 event: `INCOMING_CHAT_INTERCEPT`

And i would like to ask you (🫵) for events you would like to see

Example usage:
```py
from system.lib.minescript import *
import eventlib # Put it anywhere before instancing event queue ("EventQueue()")

events = EventQueue()
events.register_incoming_chat_interceptor()

while True:
    event = events.get()
    if event.type == EventType.INCOMING_CHAT_INTERCEPT:
        echo(f"Recieved: {event.message}")
```
