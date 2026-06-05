## Table of contents
### Events
- [Incoming chat interceptor](https://github.com/SmaertBoty/Minescript/blob/main/eventlib/Docs.md#incoming-chat-interceptor)
- [Entity totem popped](https://github.com/SmaertBoty/Minescript/blob/main/eventlib/Docs.md#entity-totem-popped)
- [Entity died](https://github.com/SmaertBoty/Minescript/blob/main/eventlib/DOCS.md#entity-died)
- [Server particle](https://github.com/SmaertBoty/Minescript/blob/main/eventlib/DOCS.md#server-particle)
### Data Types
- EntityData -> https://minescript.net/docs#entitydata

### Syntax
Use `from eventlib import *` for syntax checking

## Listeners
### Incoming chat interceptor
Intercepts all incoming messages, before they reach other parts of the client
```
listener: register_incoming_chat_interceptor()
type: EventType.INCOMING_CHAT_INTERCEPT
message: str
```

### Entity totem popped
Triggers when a totem of an entity is "popped"
```
listener: register_totem_popped_listener()
type: EventType.ENTITY_TOTEM_POPPED
entity: EntityData
```

### Entity died
Triggers when an entity dies
```
listener: register_entity_died_listener()
type: EventType.ENTITY_DIED
entity: EntityData
```

### Server particle
Triggers when a particle from the server appears
```
listener: register_server_particle_listener()
type: EventType.SERVER_PARTICLE
particle: str
x: float
y: float
z: float
```

### Health change
Triggeres when the health of the local player changes
```
listener: register_health_change_listener()
health: float
```

### Food change
Triggeres when the hunger or saturation of the local player changes
```
listener: register_food_change_listener()
hunger: float
saturation: float
```
