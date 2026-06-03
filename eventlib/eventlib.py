import system.lib.minescript as m
from system.lib.minescript import *
from threading import Thread
from system.lib.java import eval_pyjinn_script as eps
from time import sleep

script = eps(
r"""
mc = JavaClass("net.minecraft.client.Minecraft").getInstance()
ClientboundPlayerChatPacket = JavaClass("net.minecraft.network.protocol.game.ClientboundPlayerChatPacket")
ClientboundSystemChatPacket = JavaClass("net.minecraft.network.protocol.game.ClientboundSystemChatPacket")
ClientboundEntityEventPacket = JavaClass("net.minecraft.network.protocol.game.ClientboundEntityEventPacket")
ClientboundLevelParticlesPacket = JavaClass("net.minecraft.network.protocol.game.ClientboundLevelParticlesPacket")
BuiltInRegistries = JavaClass("net.minecraft.core.registries.BuiltInRegistries")
System = JavaClass("java.lang.System")
incoming_intercept_queue = []
totem_popped_queue = []
entity_died_queue = []
particle_queue = []
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
def get_entity_died_queue():
    global entity_died_queue
    out = entity_died_queue
    entity_died_queue = []
    return str(out)
def get_particle_queue():
    global particle_queue
    out = particle_queue
    particle_queue = []
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
        elif int(event.packet.getEventId()) == 3: entity_died_queue.append(event.packet.getEntity(mc.level).getStringUUID())
    elif isinstance(event.packet, ClientboundLevelParticlesPacket): particle_queue.append(f"{BuiltInRegistries.PARTICLE_TYPE.getKey(event.packet.getParticle().getType()).toString()};{event.packet.getX()};{event.packet.getY()};{event.packet.getZ()}")
add_event_listener("clientbound_packet",s2c)
""")

get_incoming_intercept_queue = script.get("get_incoming_intercept_queue")
get_totem_popped_queue = script.get("get_totem_popped_queue")
get_entity_died_queue = script.get("get_entity_died_queue")
get_particle_queue = script.get("get_particle_queue")

class INCOMING_CHAT_INTERCEPT:
    def __init__(self,type,message):
        self.type = type
        self.message = message

class ENTITY_TOTEM_POPPED:
    def __init__(self,type,entity):
        self.type = type
        self.entity = entity

class ENTITY_DIED:
    def __init__(self,type,entity):
        self.type = type
        self.entity = entity

class SERVER_PARTICLE:
    def __init__(self,type,particle):
        self.type = type
        self.particle = particle

class Particle:
    def __init__(self,type,x,y,z):
        self.type = type
        self.position = (float(x),float(y),float(z))

m.EventType.INCOMING_CHAT_INTERCEPT = "incoming_chat_intercept"
m._EVENT_CONSTRUCTORS["incoming_chat_intercept"] = INCOMING_CHAT_INTERCEPT

m.EventType.ENTITY_TOTEM_POPPED = "entity_totem_popped"
m._EVENT_CONSTRUCTORS["entity_totem_popped"] = ENTITY_TOTEM_POPPED

m.EventType.ENTITY_DIED = "entity_died"
m._EVENT_CONSTRUCTORS["entity_died"] = ENTITY_DIED

m.EventType.SERVER_PARTICLE = "server_particle"
m._EVENT_CONSTRUCTORS["server_particle"] = SERVER_PARTICLE

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

def register_entity_died_listener(self):
    def worker():
        while True:
            events = eval(get_entity_died_queue())
            for event in events:
                self.queue.put({
                    "type": m.EventType.ENTITY_DIED,
                    "entity": [e for e in entities() if e.uuid == event][0]
                })
    Thread(target=worker, daemon=True).start()

def register_server_particle_listener(self):
    def worker():
        while True:
            events = eval(get_particle_queue())
            for event in events:
                self.queue.put({
                    "type": m.EventType.SERVER_PARTICLE,
                    "particle": Particle(*event.split(";"))
                })
    Thread(target=worker, daemon=True).start()

m.EventQueue.register_incoming_chat_interceptor = register_incoming_chat_interceptor
m.EventQueue.register_totem_popped_listener = register_totem_popped_listener
m.EventQueue.register_entity_died_listener = register_entity_died_listener
m.EventQueue.register_server_particle_listener = register_server_particle_listener