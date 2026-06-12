import system.lib.minescript as m
import sys
if int("".join([n for n in m.version_info().minescript if n.isdigit()])) < 5011: sys.exit("[Eventlib] Please update to 5.0b11!")

from system.lib.minescript import *
from threading import Thread
from system.lib.java import eval_pyjinn_script as eps
import socket
import json
import uuid
from queue import Queue as qQ
from typing import TYPE_CHECKING
from dataclasses import dataclass
from time import time

try: identifier = str(uuid.uuid8())
except: identifier = str(uuid.uuid1())

bridge = socket.socket()
bridge.bind(("127.0.0.1", 0))
bridge.listen(1)
port = bridge.getsockname()[1]

def __serve_listener__():
    while True:
        line = file.readline()
        if not line: continue
        try: 
            event = json.loads(line)
            if event["event"] == "intercept_incoming_chat":
                queues = registered_incoming_intercept.copy()
                for queue in queues:
                    queue.put(
                        {
                        "type": m.EventType.INCOMING_CHAT_INTERCEPT,
                        "message": event["text"],
                        "json": event["json"]
                    })
            elif event["event"] == "entity_totem_popped":
                queues = registered_totem_popped.copy()
                for queue in queues:
                    queue.put({
                        "type": m.EventType.ENTITY_TOTEM_POPPED,
                        "entity": [e for e in entities() if e.uuid == event["uuid"]][0]
                    })
            elif event["event"] == "entity_died":
                queues = registered_entity_died.copy()
                for queue in queues:
                    queue.put({
                        "type": m.EventType.ENTITY_DIED,
                        "entity": [e for e in entities() if e.uuid == event["uuid"]][0]
                    })
            elif event["event"] == "server_particle":
                queues = registered_particle.copy()
                for queue in queues:
                    queue.put({
                        "type": m.EventType.SERVER_PARTICLE,
                        "particle": event["particle"],
                        "position": (float(event["x"]),float(event["y"]),float(event["z"]))
                    })
            elif event["event"] == "client_tick":
                queues = registered_client_tick.copy()
                for queue in queues:
                    queue.put({
                        "type": m.EventType.CLIENT_TICK,
                        "tick": int(event["tick"])
                    })
            elif event["event"] == "health_change":
                queues = registered_client_tick.copy()
                for queue in queues:
                    queue.put({
                        "type": m.EventType.HEALTH_CHANGE,
                        "health": float(event["health"])
                    })
            elif event["event"] == "food_change":
                queues = registered_food_change.copy()
                for queue in queues:
                    queue.put({
                        "type": m.EventType.FOOD_CHANGE,
                        "hunger": float(event["food"]),
                        "saturation": float(event["saturation"])
                    })
            elif event["event"] == "actionbar_change":
                queues = registered_actionbar_change.copy()
                for queue in queues:
                    queue.put({
                        "type": m.EventType.ACTIONBAR_CHANGE,
                        "message": event["message"]
                    })
            elif event["event"] == "chat_event":
                queues = registered_chat.copy()
                for queue in queues:
                    queue.put({
                        "type": m.EventType.CHAT,
                        "message": event["text"],
                        "json": event["json"],
                        "time": time()
                    })
            elif event["event"] == "key_event":
                queues = registered_key.copy()
                for queue in queues:
                    queue.put({
                        "type":m.EventType.KEY,
                        "time": time(),
                        "key": int(event["key"]),
                        "pretty_key": event["pretty_key"],
                        "scan_code": int(event["scan_code"]),
                        "action": int(event["action"]),
                        "modifiers": int(event["modifiers"]),
                        "screen": event["screen"]
                    })
            queues = []
        except: log(f"Malformed json event: '{line}'")

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
mappings = JavaClass("net.minescript.common.Minescript").mappingsLoader.get()
ComponentSerialization = JavaClass("net.minecraft.network.chat.ComponentSerialization")
GsonBuilder = JavaClass("com.google.gson.GsonBuilder")
JsonOps = JavaClass("com.mojang.serialization.JsonOps")
RegistryOps = JavaClass("net.minecraft.resources.RegistryOps")
InputConstants = JavaClass("com.mojang.blaze3d.platform.InputConstants")
KeyEvent = JavaClass("net.minecraft.client.input.KeyEvent")

def reflect_field(_class, field_name, raw=False):
    clss = _class.getClass()
    f = mappings.getRuntimeFieldName(clss, field_name)
    field = clss.getDeclaredField(f)
    field.setAccessible(True)
    if not raw: return field.get(_class)
    else: return field

identifier = '""" + identifier + r"""'
if "eventlib" not in __script__.vars["game"]:
    __script__.vars["game"]["eventlib"] = {}
__script__.vars["game"]["eventlib"][identifier] = {"intercept_incoming_chat":{"state":False,"startswith":""},"entity_totem_popped":False,"entity_died":False,"server_particle":False,"client_tick":False,"health_change":False,"food_change":False,"actionbar_change":False,"chat_listener":False,"key_listener":False}
bridge = Socket("127.0.0.1", """ + str(port) + r""")
writer = BufferedWriter(OutputStreamWriter(bridge.getOutputStream(), StandardCharsets.UTF_8))
hp = player_health()
food = [mc.player.getFoodData().getFoodLevel(),mc.player.getFoodData().getSaturationLevel()]
ab_timestamp_predicted = reflect_field(mc.gui,"overlayMessageTime")

def add_event(event):
    writer.write(event + "\n")
    writer.flush()

def s2c(event):
    if __script__.vars["game"]["eventlib"][identifier]["intercept_incoming_chat"]["state"] or __script__.vars["game"]["eventlib"][identifier]["chat_listener"]:
        if isinstance(event.packet, ClientboundSystemChatPacket):
            if event.packet.overlay(): return
            comp = event.packet.content()
            dat = event.packet.content().getString()
            json_string = GsonBuilder().create().toJson(ComponentSerialization.CODEC.encodeStart(RegistryOps.create(JsonOps.INSTANCE, mc.level.registryAccess()),comp).getOrThrow())
        elif isinstance(event.packet, ClientboundPlayerChatPacket):
            dat = event.packet.body().content()
            comp = event.packet.body()
            json_string = '{"text":"' + dat + '"}'
        else: return
        if __script__.vars["game"]["eventlib"][identifier]["intercept_incoming_chat"]["state"]:
            if dat.startswith(__script__.vars["game"]["eventlib"][identifier]["intercept_incoming_chat"]["startswith"]):
                add_event('{"event":"intercept_incoming_chat","text":"' + dat + '","json":' + json_string + '}')
                event.cancel()
                field = reflect_field(mc.player.connection,"nextChatIndex",True)
                field.setInt(mc.player.connection, field.get(mc.player.connection)+1)
        elif __script__.vars["game"]["eventlib"][identifier]["chat_listener"]:
            add_event('{"event":"chat_event","text":"' + dat + '","json":' + json_string + '}')

    if isinstance(event.packet, ClientboundEntityEventPacket):
        if __script__.vars["game"]["eventlib"][identifier]["entity_totem_popped"]:
            if int(event.packet.getEventId()) == 35: 
                add_event('{"event":"entity_totem_popped","uuid":"' + event.packet.getEntity(mc.level).getStringUUID() + '"}')
        if __script__.vars["game"]["eventlib"][identifier]["entity_died"]:
            if int(event.packet.getEventId()) == 3: 
                add_event('{"event":"entity_died","uuid":"' + event.packet.getEntity(mc.level).getStringUUID() + '"}')
    
    if __script__.vars["game"]["eventlib"][identifier]["server_particle"]:
        if isinstance(event.packet, ClientboundLevelParticlesPacket): 
            add_event('{"event":"server_particle","particle":"' + BuiltInRegistries.PARTICLE_TYPE.getKey(event.packet.getParticle().getType()).toString() + '","x":str(event.packet.getX()),"y":str(event.packet.getY()),"z":str(event.packet.getZ())}')

def key_event(event):
    if __script__.vars["game"]["eventlib"][identifier]["key_listener"]:
        pretty_key = InputConstants.getKey(KeyEvent(event.key,event.scan_code,event.modifiers)).getDisplayName().getString()
        add_event('{"event":"key_event","key":' + str(event.key) + ',"pretty_key":"' + str(pretty_key) + '","scan_code":' + str(event.scan_code) + ',"action":' + str(event.action) + ',"modifiers":' + str(event.modifiers) + ',"screen":"' + str(event.screen) + '"}')

def tick(event):
    global hp, food, ab_timestamp_predicted
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
    if __script__.vars["game"]["eventlib"][identifier]["actionbar_change"]:
        try: nab = reflect_field(mc.gui,"overlayMessageString").getString()
        except: nab = None
        time = reflect_field(mc.gui,"overlayMessageTime")
        if time != ab_timestamp_predicted-1 and time > 0:
            add_event('{"event":"actionbar_change","message":"' + nab + '"}')
        ab_timestamp_predicted = time
    
add_event_listener("tick",tick)
add_event_listener("clientbound_packet",s2c)
add_event_listener("key",key_event)
""")
conn, _ = bridge.accept()
file = conn.makefile()

registered_incoming_intercept = []
registered_totem_popped = []
registered_entity_died = []
registered_particle = []
registered_client_tick = []
registered_health_change = []
registered_food_change = []
registered_actionbar_change = []
registered_chat = []
registered_key = []

Thread(target=__serve_listener__,daemon=True).start()

@dataclass
class INCOMING_CHAT_INTERCEPT:
    type:str
    message:str
    json:dict

@dataclass
class ENTITY_TOTEM_POPPED:
    type:str
    entity:EntityData

@dataclass
class ENTITY_DIED:
    type:str
    entity:EntityData

@dataclass
class SERVER_PARTICLE:
    type:str
    particle:str
    position:tuple[float,float,float]

@dataclass
class CLIENT_TICK:
    type:str
    tick:int

@dataclass
class HEALTH_CHANGE:
    type:str
    health:float

@dataclass
class FOOD_CHANGE:
    type:str
    hunger:float
    saturation:float

@dataclass
class ACTIONBAR_CHANGE:
    type:str
    message:str

@dataclass
class EventlibChatEvent(m.ChatEvent):
    type:str
    time:float
    message:str
    json:dict=None

@dataclass
class EventlibKeyEvent(m.KeyEvent):
    type: str
    time: float
    key: int
    pretty_key: str = None
    scan_code: int
    action: int
    modifiers: int
    screen: str

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

m.EventType.ACTIONBAR_CHANGE = "actionbar_change"
m._EVENT_CONSTRUCTORS["actionbar_change"] = ACTIONBAR_CHANGE

def register_incoming_chat_interceptor(self,*,startswith:str=""):
    execute(fr"""\eval '0' '__script__.vars["game"]["eventlib"]["{identifier}"]["intercept_incoming_chat"] = {"{"}"state":True,"startswith":"{startswith}"{"}"}'""")
    self.eventlib_listeners.append("intercept_incoming_chat")
    registered_incoming_intercept.append(self.queue)

def register_totem_popped_listener(self):
    execute(fr"""\eval '0' '__script__.vars["game"]["eventlib"]["{identifier}"]["entity_totem_popped"] = True'""")
    self.eventlib_listeners.append("entity_totem_popped")
    registered_totem_popped.append(self.queue)

def register_entity_died_listener(self):
    execute(fr"""\eval '0' '__script__.vars["game"]["eventlib"]["{identifier}"]["entity_died"] = True'""")
    self.eventlib_listeners.append("entity_died")
    registered_entity_died.append(self.queue)

def register_server_particle_listener(self):
    execute(fr"""\eval '0' '__script__.vars["game"]["eventlib"]["{identifier}"]["server_particle"] = True'""")
    self.eventlib_listeners.append("server_particle")
    registered_particle.append(self.queue)

def register_client_tick_listener(self):
    execute(fr"""\eval '0' '__script__.vars["game"]["eventlib"]["{identifier}"]["client_tick"] = True'""")
    self.eventlib_listeners.append("client_tick")
    registered_client_tick.append(self.queue)

def register_health_change_listener(self):
    execute(fr"""\eval '0' '__script__.vars["game"]["eventlib"]["{identifier}"]["health_change"] = True'""")
    self.eventlib_listeners.append("health_change")
    registered_health_change.append(self.queue)

def register_food_change_listener(self):
    execute(fr"""\eval '0' '__script__.vars["game"]["eventlib"]["{identifier}"]["food_change"] = True'""")
    self.eventlib_listeners.append("food_change")
    registered_food_change.append(self.queue)

def register_actionbar_change_listener(self):
    execute(fr"""\eval '0' '__script__.vars["game"]["eventlib"]["{identifier}"]["actionbar_change"] = True'""")
    self.eventlib_listeners.append("actionbar_change")
    registered_actionbar_change.append(self.queue)

def eventlib_register_chat_listener(self,*,eventlib=False):
    if eventlib: 
        execute(fr"""\eval '0' '__script__.vars["game"]["eventlib"]["{identifier}"]["chat_listener"] = True'""")
        self.eventlib_listeners.append("chat_listener")
        registered_chat.append(self.queue)
    else: self._register(m.EventType.CHAT, m._register_chat_message_listener)

def eventlib_register_key_listener(self,*,eventlib=False):
    if eventlib:
        execute(fr"""\eval '0' '__script__.vars["game"]["eventlib"]["{identifier}"]["key_listener"] = True'""")
        self.eventlib_listeners.append("key_listener")
        registered_key.append(self.queue)
    else: self._register(m.EventType.KEY, m._register_key_listener)

def unregister_all(self):
    for event in self.eventlib_listeners:
        if event != "intercept_incoming_chat": execute(fr"""\eval '0' '__script__.vars["game"]["eventlib"]["{identifier}"]["{event}"] = False'""")
        else: execute(fr"""\eval '0' '__script__.vars["game"]["eventlib"]["{identifier}"]["{event}"]["state"] = False'""")
    self.eventlib_listeners = []
    listener_ids = self.event_listener_ids
    self.event_listener_ids = []
    for listener_id in listener_ids:
      m._unregister_event_handler(listener_id)

m.EventQueue.register_incoming_chat_interceptor = register_incoming_chat_interceptor
m.EventQueue.register_totem_popped_listener = register_totem_popped_listener
m.EventQueue.register_entity_died_listener = register_entity_died_listener
m.EventQueue.register_server_particle_listener = register_server_particle_listener
m.EventQueue.register_client_tick_listener = register_client_tick_listener
m.EventQueue.register_health_change_listener = register_health_change_listener
m.EventQueue.register_food_change_listener = register_food_change_listener
m.EventQueue.register_actionbar_change_listener = register_actionbar_change_listener
m.EventQueue.register_chat_listener = eventlib_register_chat_listener
m.EventQueue.register_key_listener = eventlib_register_key_listener
m._EVENT_CONSTRUCTORS["chat"] = EventlibChatEvent
m._EVENT_CONSTRUCTORS["key"] = EventlibKeyEvent

m.EventQueue.unregister_all = unregister_all
m.EventQueue.eventlib_listeners = []

if TYPE_CHECKING:
    class EventQueue(m.EventQueue(),m.EventQueue):
        eventlib_listeners = []
        def register_incoming_chat_interceptor(self,*,startswith:str=""): ...
        def register_totem_popped_listener(self): ...
        def register_entity_died_listener(self): ...
        def register_server_particle_listener(self): ...
        def register_client_tick_listener(self): ...
        def register_health_change_listener(self): ...
        def register_food_change_listener(self): ...
        def register_actionbar_change_listener(self): ...
        def get(self, block: bool = True, timeout: float = None) -> Event|None:
            """Gets the next event in the queue.

            Args:
              block: if `True`, block until an event fires
              timeout: timeout in seconds to wait for an event if `block` is `True`
        
            Returns:
              subclass-dependent event
        
            Raises:
              `queue.Empty` if `block` is `True` and `timeout` expires, or `block` is `False` and
              queue is empty.
            """
        def register_chat_listener(self,*,eventlib:bool=False):
            """Registers listener for `EventType.CHAT` events as `ChatEvent`.
        
            Example:
            ```
              with EventQueue() as event_queue:
                event_queue.register_chat_listener()
                while True:
                  event = event_queue.get()
                  if event.type == EventType.CHAT:
                    if not event.message.startswith("> "):
                      echo(f"> Got chat message: {event.message}")
            ```
            If `eventlib` is `True`, extra data will be attached
            """
        def register_key_listener(self,*,eventlib:bool=False):
            """Registers listener for `EventType.KEY` events as `KeyEvent`.
            Example:
            ```
              with EventQueue() as event_queue:
                event_queue.register_key_listener()
                while True:
                  event = event_queue.get()
                  if event.type == EventType.KEY:
                    if event.action == 0:
                      action = 'up'
                    elif event.action == 1:
                      action = 'down'
                    else:
                      action = 'repeat'
                    echo(f"Got key {action} with code {event.key}")
            ```
            If `eventlib` is `True`, extra data will be attached
            """
        def unregister_all(): ...
    class EventType(m._EventType):
        INCOMING_CHAT_INTERCEPT:str = "incoming_chat_intercept"
        ENTITY_TOTEM_POPPED:str = "entity_totem_popped"
        ENTITY_DIED:str = "entity_died"
        SERVER_PARTICLE:str = "server_particle"
        CLIENT_TICK:str = "client_tick"
        HEALTH_CHANGE:str = "health_change"
        FOOD_CHANGE:str = "food_change"
        ACTIONBAR_CHANGE:str = "actionbar_change"
    class Event:
        type:str
        time:float
        message:str
        entity:EntityData
        position:BlockPos|Vector3f
        old_state:str
        new_state:str
        player_uuid:str
        item:ItemStack
        amount:int
        entity_uuid:str
        cause_uuid:str
        source:str
        blockpack_base64:str
        loaded:bool
        x_min:int
        z_min:int
        x_max:int
        z_max:int
        connected:bool
        json:dict
        key:int
        pretty_key:str
