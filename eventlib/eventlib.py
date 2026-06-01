import system.lib.minescript as m
from system.lib.minescript import *
from threading import Thread
from system.lib.java import eval_pyjinn_script as eps
import uuid

identifier = uuid.uuid8()

script = eps(
fr"""
ClientboundPlayerChatPacket = JavaClass("net.minecraft.network.protocol.game.ClientboundPlayerChatPacket")
ClientboundSystemChatPacket = JavaClass("net.minecraft.network.protocol.game.ClientboundSystemChatPacket")
identifier = "{identifier}"
if "incoming_intercept_queue" not in __script__.vars["game"]:
    __script__.vars["game"]["incoming_intercept_queue"] =  {"{"}{"}"}
if identifier not in __script__.vars["game"]["incoming_intercept_queue"]:
    __script__.vars["game"]["incoming_intercept_queue"][identifier] = []
def get_incoming_intercept_queue():
    out = __script__.vars["game"]["incoming_intercept_queue"][identifier]
    __script__.vars["game"]["incoming_intercept_queue"][identifier] = []
    return str(out)
def s2c(event):
    if isinstance(event.packet, ClientboundSystemChatPacket):
        __script__.vars["game"]["incoming_intercept_queue"][identifier].append(event.packet.content().getString())
        event.cancel()
    elif isinstance(event.packet, ClientboundPlayerChatPacket):
        try: __script__.vars["game"]["incoming_intercept_queue"][identifier].append(event.packet.unsignedContent().getString())
        except: __script__.vars["game"]["incoming_intercept_queue"][identifier].append(event.packet.body().content())
        event.cancel()
add_event_listener("clientbound_packet",s2c)
""")

get_incoming_intercept_queue = script.get("get_incoming_intercept_queue")

class INCOMING_CHAT_INTERCEPT:
    def __init__(self,type,message):
        self.type = type
        self.message = message

m.EventType.INCOMING_CHAT_INTERCEPT = "incoming_chat_intercept"
m._EVENT_CONSTRUCTORS["incoming_chat_intercept"] = INCOMING_CHAT_INTERCEPT

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

setattr(m.EventQueue, "register_incoming_chat_interceptor", register_incoming_chat_interceptor)
