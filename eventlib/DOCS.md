### Table of contents
## Events
- [Incoming chat interceptor](https://github.com/SmaertBoty/Minescript/blob/main/eventlib/Docs.md#incoming-chat-interceptor)
- [Entity totem popped](https://github.com/SmaertBoty/Minescript/blob/main/eventlib/Docs.md#entity-totem-popped)
- Entity died
- Server particle
## Data Types
- EntityData -> https://minescript.net/docs#entitydata
- Packet:
```
type: str
position: tuple(float, float, float)
```


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
particle: Particle
```
