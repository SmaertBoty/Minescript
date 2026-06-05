import system.lib.minescript as m
from system.lib.minescript import *
from threading import Thread
from system.lib.java import eval_pyjinn_script as eps
import socket
import json
import uuid
from queue import Queue as qQ
from typing import TYPE_CHECKING

identifier = str(uuid.uuid8())

bridge = socket.socket()
bridge.bind(("127.0.0.1", 0))
bridge.listen(1)
port = bridge.getsockname()[1]

def __serve_listener__():
    while True:
        line = file.readline()
        if not line:
            continue
        try: 
            event = json.loads(line)
            if event["event"] == "intercept_incoming_chat":
                incoming_intercept_queue.put(event["message"])
            elif event["event"] == "entity_totem_popped":
                totem_popped_queue.put(event["uuid"])
            elif event["event"] == "entity_died":
                entity_died_queue.put(event["uuid"])
            elif event["event"] == "server_particle":
                particle_queue.put((event["particle"],float(event["x"]),float(event["y"]),float(event["z"])))
            elif event["event"] == "client_tick":
                client_tick_queue.put(int(event["tick"]))
            elif event["event"] == "health_change":
                health_change_queue.put(float(event["health"]))
            elif event["food_change"]:
                food_change_queue.put((float(event[""])))
        except: log("Malformed json event:", f"'{line}'")

script = eps(
r"""
mc = JavaClass("net.minecraft.client.Minecraft").getInstance()
ClientboundPlayerChatPacket = JavaClass("net.minecraft.network.protocol.game.ClientboundPlayerChatPacket")
ClientboundSystemChatPacket = JavaClass("net.minecraft.network.protocol.game.ClientboundSystemChatPacket")
ClientboundEntityEventPacket = JavaClass("net.minecraft.network.protocol.game.ClientboundEntityEventPacket")
ClientboundLevelParticlesPacket = JavaClass("net.minecraft.network.protocol.game.ClientboundLevelParticlesPacket")
BuiltInRegistries = JavaClass("net.minecraft.core.registries.BuiltInRegistries")
BufferedWriter = JavaClass("java.io.BufferedWriter")
OutputStreamWriter = JavaClass("java.io.OutputStreamWriter")
Socket = JavaClass("java.net.Socket")
StandardCharsets = JavaClass("java.nio.charset.StandardCharsets")

identifier = '""" + identifier + r"""'
if "eventlib" not in __script__.vars["game"]:
    __script__.vars["game"]["eventlib"] = {}
__script__.vars["game"]["eventlib"][identifier] = {"intercept_incoming_chat":False,"entity_totem_popped":False,"entity_died":False,"server_particle":False,"client_tick":False,"health_change":False,"food_change":False}
bridge = Socket("127.0.0.1", """ + str(port) + r""")
writer = BufferedWriter(OutputStreamWriter(bridge.getOutputStream(), StandardCharsets.UTF_8))
hp = player_health()
food = [mc.player.getFoodData().getFoodLevel(),mc.player.getFoodData().getSaturationLevel()]

def add_event(event):
    writer.write(event + "\n")
    writer.flush()

def s2c(event):
    if __script__.vars["game"]["eventlib"][identifier]["intercept_incoming_chat"]:
        if isinstance(event.packet, ClientboundSystemChatPacket):
            add_event('{"event":"intercept_incoming_chat","message":"' + event.packet.content().getString() + '"}')
            event.cancel()
        elif isinstance(event.packet, ClientboundPlayerChatPacket):
            try: add_event('{"event":"intercept_incoming_chat","message":"' + event.packet.unsignedContent().getString() + '"}')
            except: add_event('{"event":"intercept_incoming_chat","message":"' + event.packet.body().content() + '"}')
            event.cancel()

    if isinstance(event.packet, ClientboundEntityEventPacket):
        if __script__.vars["game"]["eventlib"][identifier]["entity_totem_popped"]:
            if int(event.packet.getEventId()) == 35: add_event('{"event":"entity_totem_popped","uuid":"' + event.packet.getEntity(mc.level).getStringUUID() + '"}')
        if __script__.vars["game"]["eventlib"][identifier]["entity_died"]:
            if int(event.packet.getEventId()) == 3: add_event('{"event":"entity_died","uuid":"' + event.packet.getEntity(mc.level).getStringUUID() + '"}')
    
    if __script__.vars["game"]["eventlib"][identifier]["server_particle"]:
        if isinstance(event.packet, ClientboundLevelParticlesPacket): add_event('{"event":"server_particle","particle":"' + BuiltInRegistries.PARTICLE_TYPE.getKey(event.packet.getParticle().getType()).toString() + '","x":str(event.packet.getX()),"y":str(event.packet.getY()),"z":str(event.packet.getZ())}')

def tick(event):
    global hp, food
    if __script__.vars["game"]["eventlib"][identifier]["client_tick"]:
        add_event('{"event":"client_tick","tick":' + str(world_info().game_ticks) + '}')
    if __script__.vars["game"]["eventlib"][identifier]["health_change"]:
        if hp != player_health():
            add_event('{"event":"health_change","health":' + str(player_health()) + '}')
            hp = player_health()
    if __script__.vars["game"]["eventlib"][identifier]["food_change"]:
        new_food = [mc.player.getFoodData().getFoodLevel(),mc.player.getFoodData().getSaturationLevel()]
        if food != new_food:
            add_event('{"event":"food_change","food":' + str(new_food[0]) + ',"saturation":' + str(new_food[1]) + '}')
            food = new_food
    
add_event_listener("tick",tick)
add_event_listener("clientbound_packet",s2c)
""")
conn, _ = bridge.accept()
file = conn.makefile()

incoming_intercept_queue = qQ()
totem_popped_queue = qQ()
entity_died_queue = qQ()
particle_queue = qQ()
client_tick_queue = qQ()
health_change_queue = qQ()
food_change_queue = qQ()

Thread(target=__serve_listener__).start()

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

class CLIENT_TICK:
    def __init__(self,type,tick):
        self.type = type
        self.tick = tick

class HEALTH_CHANGE:
    def __init__(self,type,health):
        self.type = type
        self.health = health

class FOOD_CHANGE:
    def __init__(self,hunger,saturation):
        self.hunger = hunger
        self.saturation = saturation

m.EventType.INCOMING_CHAT_INTERCEPT = "incoming_chat_intercept"
m._EVENT_CONSTRUCTORS["incoming_chat_intercept"] = INCOMING_CHAT_INTERCEPT

m.EventType.ENTITY_TOTEM_POPPED = "entity_totem_popped"
m._EVENT_CONSTRUCTORS["entity_totem_popped"] = ENTITY_TOTEM_POPPED

m.EventType.ENTITY_DIED = "entity_died"
m._EVENT_CONSTRUCTORS["entity_died"] = ENTITY_DIED

m.EventType.SERVER_PARTICLE = "server_particle"
m._EVENT_CONSTRUCTORS["server_particle"] = SERVER_PARTICLE

m.EventType.CLIENT_TICK = "client_tick"
m._EVENT_CONSTRUCTORS["client_tick"] = CLIENT_TICK

m.EventType.HEALTH_CHANGE = "health_change"
m._EVENT_CONSTRUCTORS["health_change"] = HEALTH_CHANGE

m.EventType.FOOD_CHANGE = "food_change"
m._EVENT_CONSTRUCTORS["food_change"] = FOOD_CHANGE

def register_incoming_chat_interceptor(self):
    execute(fr"""\eval '0' '__script__.vars["game"]["eventlib"]["{identifier}"]["intercept_incoming_chat"] = True'""")
    def worker():
        while True:
            event = incoming_intercept_queue.get()
            self.queue.put({
                "type": m.EventType.INCOMING_CHAT_INTERCEPT,
                "message": event
            })
    Thread(target=worker, daemon=True).start()

def register_totem_popped_listener(self):
    execute(fr"""\eval '0' '__script__.vars["game"]["eventlib"]["{identifier}"]["entity_totem_popped"] = True'""")
    def worker():
        while True:
            event = totem_popped_queue.get()
            self.queue.put({
                "type": m.EventType.ENTITY_TOTEM_POPPED,
                "entity": [e for e in entities() if e.uuid == event][0]
            })
    Thread(target=worker, daemon=True).start()

def register_entity_died_listener(self):
    execute(fr"""\eval '0' '__script__.vars["game"]["eventlib"]["{identifier}"]["entity_died"] = True'""")
    def worker():
        while True:
            event = entity_died_queue.get()
            self.queue.put({
                "type": m.EventType.ENTITY_DIED,
                "entity": [e for e in entities() if e.uuid == event][0]
            })
    Thread(target=worker, daemon=True).start()

def register_server_particle_listener(self):
    execute(fr"""\eval '0' '__script__.vars["game"]["eventlib"]["{identifier}"]["server_particle"] = True'""")
    def worker():
        while True:
            event = particle_queue.get()
            self.queue.put({
                "type": m.EventType.SERVER_PARTICLE,
                "particle": event[0],
                "x": event[1],
                "y": event[2],
                "z": event[3]
            })
    Thread(target=worker, daemon=True).start()

def register_client_tick_listener(self):
    execute(fr"""\eval '0' '__script__.vars["game"]["eventlib"]["{identifier}"]["client_tick"] = True'""")
    def worker():
        while True:
            event = client_tick_queue.get()
            self.queue.put({
                "type": m.EventType.CLIENT_TICK,
                "tick": event
            })
    Thread(target=worker, daemon=True).start()

def register_health_change_listener(self):
    execute(fr"""\eval '0' '__script__.vars["game"]["eventlib"]["{identifier}"]["health_change"] = True'""")
    def worker():
        while True:
            event = health_change_queue.get()
            self.queue.put({
                "type": m.EventType.HEALTH_CHANGE,
                "health": event
            })
    Thread(target=worker, daemon=True).start()

def register_food_change_listener(self):
    execute(fr"""\eval '0' '__script__.vars["game"]["eventlib"]["{identifier}"]["food_change"] = True'""")
    def worker():
        while True:
            event = health_change_queue.get()
            self.queue.put({
                "type": m.EventType.FOOD_CHANGE,
                "hunger": event[0],
                "saturation": event[1]
            })
    Thread(target=worker, daemon=True).start()

m.EventQueue.register_incoming_chat_interceptor = register_incoming_chat_interceptor
m.EventQueue.register_totem_popped_listener = register_totem_popped_listener
m.EventQueue.register_entity_died_listener = register_entity_died_listener
m.EventQueue.register_server_particle_listener = register_server_particle_listener
m.EventQueue.register_client_tick_listener = register_client_tick_listener
m.EventQueue.register_health_change_listener = register_health_change_listener
m.EventQueue.register_food_change_listener = register_food_change_listener

if TYPE_CHECKING:
    class EventQueue:
        def register_incoming_chat_interceptor(self): ...
        def register_totem_popped_listener(self): ...
        def register_entity_died_listener(self): ...
        def register_server_particle_listener(self): ...
        def register_client_tick_listener(self): ...
        def register_health_change_listener(self): ...
        def register_food_change_listener(self): ...
    EventType.INCOMING_CHAT_INTERCEPT = "incoming_chat_intercept"
    EventType.ENTITY_TOTEM_POPPED = "entity_totem_popped"
    EventType.ENTITY_DIED = "entity_died"
    EventType.SERVER_PARTICLE = "server_particle"
    EventType.CLIENT_TICK = "client_tick"
    EventType.HEALTH_CHANGE = "health_change"
    EventType.FOOD_CHANGE = "food_change"