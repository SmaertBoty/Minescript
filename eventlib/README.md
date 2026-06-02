Eventlib is a library aiming to add new events, while keeping minescripts `EventQueue`. It is a drag n' drop library, meaning you just import it, and you already have everything set up.
Requires 5.0b11 or higher

As of now, it contains: 
- `INCOMING_CHAT_INTERCEPT`
- `ENTITY_TOTEM_POPPED`

And i would like to ask you (🫵) for events you would like to see

Example usage:
```py
from system.lib.minescript import *
import eventlib # Put it anywhere before instancing event queue ("EventQueue()")

events = EventQueue()
events.register_incoming_chat_interceptor()
events.register_totem_popped_listener()

while True:
    event = events.get()
    if event.type == EventType.INCOMING_CHAT_INTERCEPT:
        echo(f"Recieved: {event.message}")
    if event.type == EventType.ENTITY_TOTEM_POPPED:
        echo("Totem popped for: " + event.entity.name)
```
