debug = False

import socket
from system.lib.java import eval_pyjinn_script as eps
import json
from threading import Thread
from system.lib.minescript import version_info

version = int("".join([n for n in version_info().minecraft if n.isdigit()]))

if not str(version).startswith("1"): version = int("99"+str(version))

version_mappings = {
    "clicktype_const": {
        (0,12111) : ("handleInventoryMouseClick","""ClickType = JavaClass("net.minecraft.world.inventory.ClickType")"""),
        (99262,999999): ("handleContainerInput","""ClickType = JavaClass("net.minecraft.world.inventory.ContainerInput")""")
    }
}

clicktype_mapping = [v for k,v in version_mappings["clicktype_const"].items() if k[0] <= version <= k[1]][0]

bridge = socket.socket()
bridge.bind(("127.0.0.1", 0))
bridge.listen(1)
port = bridge.getsockname()[1]

eps(
r"""
mc = JavaClass("net.minecraft.client.Minecraft").getInstance()
ItemStack = JavaClass("net.minecraft.world.item.ItemStack")
GsonBuilder = JavaClass("com.google.gson.GsonBuilder")
JsonOps = JavaClass("com.mojang.serialization.JsonOps")
BufferedWriter = JavaClass("java.io.BufferedWriter")
OutputStreamWriter = JavaClass("java.io.OutputStreamWriter")
Socket = JavaClass("java.net.Socket")
StandardCharsets = JavaClass("java.nio.charset.StandardCharsets")
BufferedReader = JavaClass("java.io.BufferedReader")
InputStreamReader = JavaClass("java.io.InputStreamReader")
""" + clicktype_mapping[1] + r"""
RegistryOps = JavaClass("net.minecraft.resources.RegistryOps")
InventoryScreen = JavaClass("net.minecraft.client.gui.screens.inventory.InventoryScreen")

bridge = Socket("127.0.0.1", """ + str(port) + r""")
bridge.setSoTimeout(1)
writer = BufferedWriter(OutputStreamWriter(bridge.getOutputStream(), StandardCharsets.UTF_8))
reader = BufferedReader(InputStreamReader(bridge.getInputStream(), StandardCharsets.UTF_8))

def return_call(data):
    if data is None: data = "null"
    elif data is True: data = "true"
    elif data is False: data = "false"
    writer.write(data + "\n")
    writer.flush()

def serialize_stack(itemstack):
    return GsonBuilder().create().toJson(ItemStack.CODEC.encodeStart(RegistryOps.create(JsonOps.INSTANCE, mc.level.registryAccess()), itemstack).getOrThrow())

def inventory(*_):
    out = []
    for slot in mc.player.containerMenu.slots:
        itemstack = slot.getItem()
        if str(itemstack) != "0 minecraft:air": out.append(serialize_stack(itemstack))
        else: out.append('{"id":"minecraft:air","count":0}')
    return "[" + ", ".join(out) + "]"

def pickup(slot,mouse):
    slot = int(slot)
    mouse = int(mouse)
    mc.gameMode.""" + clicktype_mapping[0] + r"""(mc.player.containerMenu.containerId, slot, mouse, ClickType.PICKUP, mc.player)

def quickmove(slot,mouse):
    slot = int(slot)
    mouse = int(mouse)
    mc.gameMode.""" + clicktype_mapping[0] + r"""(mc.player.containerMenu.containerId, slot, mouse, ClickType.QUICK_MOVE, mc.player)

def throw(slot,all):
    slot = int(slot)
    all = int(all)
    mc.gameMode.""" + clicktype_mapping[0] + r"""(mc.player.containerMenu.containerId, slot, all, ClickType.THROW, mc.player)

def swap(slot1,slot2):
    slot1 = int(slot1)
    slot2 = int(slot2)
    mc.gameMode.""" + clicktype_mapping[0] + r"""(mc.player.containerMenu.containerId, slot1, slot2, ClickType.SWAP, mc.player)

def open(*_):
    mc.setScreen(InventoryScreen(mc.player))

def close(*_):
    mc.player.closeContainer()

def get_item(slot):
    _slot = int(slot)
    for slot in mc.player.containerMenu.slots:
        if slot.getContainerSlot() == _slot: itemstack = slot.getItem()
    if str(itemstack) != "0 minecraft:air": return serialize_stack(itemstack)
    else: return '{"id":"minecraft:air","count":0}'

callables = {
"inventory":inventory,
"pickup":pickup,
"quickmove":quickmove,
"swap":swap,
"open":open,
"get_item":get_item,
"close":close,
"throw":throw
}

def frame(_):
    lines = []
    iters = 0
    while True:
        iters += 1
        if iters > 100: log("[Lib_inv] Overloaded! Exiting reader...") ; break
        try:
            line = reader.readLine()
            if line: lines.append(line)
            else: break
        except Exception as e:
            break
    for line in lines:
        cmd = line.split(":")
        if cmd[0][0] == "R": return_call(callables[cmd[0][1:]](*cmd[1].split(",")))
        else: callables[cmd[0][1:]](*cmd[1].split(","))

add_event_listener("render",frame)
""")

conn, _ = bridge.accept()
file = conn.makefile(mode="rw",encoding="utf-8")

def await_function_call(func_name,*args):
    file.write(f"R{func_name}:{",".join(args) if args else ""}\n")
    file.flush()
    while True:
        line = file.readline()
        if not line: continue
        else: break
    return line[:-1]

def noreturn_function_call(func_name,*args):
    file.write(f"N{func_name}:{",".join(args) if args else ""}\n")
    file.flush()

def inventory() -> list[dict]:
    """
    Returns the entire player inventory, as a list of dicts
    """
    return json.loads(await_function_call("inventory"))

def pickup(slot:int,mouse:int=0):
    """
    Simulate a pickup action on a slot
    """
    noreturn_function_call("pickup",str(slot),str(mouse))

def quickmove(slot:int,mouse:int=0):
    """
    Simulate a quickmove action on a slot
    """
    noreturn_function_call("quickmove",str(slot),str(mouse))

def swap(slot1:int,slot2:int):
    """
    Simulate a swap action on 2 slots
    """
    noreturn_function_call("swap",str(slot1),str(slot2))

def throw(slot:int,stack:bool=False):
    """
    Simulate a throw action on a slot
    """
    noreturn_function_call("throw",str(slot),str(1 if stack else 0))

def open():
    """
    Opens up the players inventory
    """
    noreturn_function_call("open")

def close():
    """
    Closes any open gui
    """
    noreturn_function_call("close")

def get_item(slot:int) -> dict:
    """
    Get the item from a slot
    """
    return json.loads(await_function_call("get_item",str(slot)))
