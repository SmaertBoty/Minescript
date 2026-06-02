### Table of contents:
- [Incoming chat interceptor](https://github.com/SmaertBoty/Minescript/blob/main/eventlib/Docs.md#incoming-chat-interceptor)
- [Entity totem popped](https://github.com/SmaertBoty/Minescript/blob/main/eventlib/Docs.md#entity-totem-popped)

### Incoming chat interceptor
Intercepts all incoming messages, before they reach other parts of the client
```
type: EventType.INCOMING_CHAT_INTERCEPT
message: str
```

### Entity totem popped
Triggers when a totem of an entity is "popped"
```
type: EventType.ENTITY_TOTEM_POPPED
entity: EntityData
```
