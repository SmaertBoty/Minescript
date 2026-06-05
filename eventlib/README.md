Eventlib is a library aiming to add new events, while keeping minescripts `EventQueue`. It is a drag n' drop library, meaning you just import it, and you already have everything set up.
Requires 5.0b11 or higher, and mappings (`\install_mappings`)

As of now, it contains: 
- `INCOMING_CHAT_INTERCEPT`
- `ENTITY_TOTEM_POPPED`
- `ENTITY_DIED`
- `SERVER_PARTICLE`
- `CLIENT_TICK`
- `HEALTH_CHANGE`
- `FOOD_CHANGE`

And i would like to ask you (🫵) for events you would like to see

Docs: https://github.com/SmaertBoty/Minescript/blob/main/eventlib/DOCS.md

Example usage:
```py
from system.lib.minescript import *
import eventlib # Put it anywhere before instancing event queue ("EventQueue()")

events = EventQueue()
events.register_incoming_chat_interceptor()
events.register_totem_popped_listener()
events.register_entity_died_listener()
events.register_server_particle_listener()

while True:
    event = events.get()
    if event.type == EventType.INCOMING_CHAT_INTERCEPT:
        echo(f"Recieved: {event.message}")
    if event.type == EventType.ENTITY_TOTEM_POPPED:
        echo("Totem popped for: " + event.entity.name)
    if event.type == EventType.ENTITY_DIED:
        echo(f"{event.entity.name} died!")
    if event.type == EventType.SERVER_PARTICLE:
        echo(f"Particle {event.particle.type} appeared at {event.particle.position}")
```
