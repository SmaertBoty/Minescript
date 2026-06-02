import system.lib.minescript as m
from system.lib.minescript import *
from threading import Thread
from system.lib.java import eval_pyjinn_script as eps

script = eps(
fr"""
mc = JavaClass("net.minecraft.client.Minecraft").getInstance()
ClientboundPlayerChatPacket = JavaClass("net.minecraft.network.protocol.game.ClientboundPlayerChatPacket")
ClientboundSystemChatPacket = JavaClass("net.minecraft.network.protocol.game.ClientboundSystemChatPacket")
ClientboundEntityEventPacket = JavaClass("net.minecraft.network.protocol.game.ClientboundEntityEventPacket")
System = JavaClass("java.lang.System")
incoming_intercept_queue = []
totem_popped_queue = []
def get_incoming_intercept_queue():
    global incoming_intercept_queue
    out = incoming_intercept_queue
    incoming_intercept_queue = []
    return str(out)
def get_totem_popped_queue():
    global totem_popped_queue
    out = totem_popped_queue
    totem_popped_queue = []
    return str(out)
def s2c(event):
    if isinstance(event.packet, ClientboundSystemChatPacket):
        incoming_intercept_queue.append(event.packet.content().getString())
        event.cancel()
    elif isinstance(event.packet, ClientboundPlayerChatPacket):
        try: incoming_intercept_queue.append(event.packet.unsignedContent().getString())
        except: incoming_intercept_queue.append(event.packet.body().content())
        event.cancel()
    elif isinstance(event.packet, ClientboundEntityEventPacket):
        if int(event.packet.getEventId()) == 35: totem_popped_queue.append(event.packet.getEntity(mc.level).getStringUUID())
add_event_listener("clientbound_packet",s2c)
""")

get_incoming_intercept_queue = script.get("get_incoming_intercept_queue")
get_totem_popped_queue = script.get("get_totem_popped_queue")

class INCOMING_CHAT_INTERCEPT:
    def __init__(self,type,message):
        self.type = type
        self.message = message

class ENTITY_TOTEM_POPPED:
    def __init__(self,type,entity):
        self.type = type
        self.entity = entity

m.EventType.INCOMING_CHAT_INTERCEPT = "incoming_chat_intercept"
m._EVENT_CONSTRUCTORS["incoming_chat_intercept"] = INCOMING_CHAT_INTERCEPT

m.EventType.ENTITY_TOTEM_POPPED = "entity_totem_popped"
m._EVENT_CONSTRUCTORS["entity_totem_popped"] = ENTITY_TOTEM_POPPED

def register_incoming_chat_interceptor(self):
    def worker():
        while True:
            events = eval(get_incoming_intercept_queue())
            for event in events:
                self.queue.put({
                    "type": m.EventType.INCOMING_CHAT_INTERCEPT,
                    "message": event
                })
    Thread(target=worker, daemon=True).start()

def register_totem_popped_listener(self):
    def worker():
        while True:
            events = eval(get_totem_popped_queue())
            for event in events:
                self.queue.put({
                    "type": m.EventType.ENTITY_TOTEM_POPPED,
                    "entity": [e for e in entities() if e.uuid == event][0]
                })
    Thread(target=worker, daemon=True).start()

setattr(m.EventQueue, "register_incoming_chat_interceptor", register_incoming_chat_interceptor)
setattr(m.EventQueue, "register_totem_popped_listener", register_totem_popped_listener)