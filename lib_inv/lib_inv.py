import socket
from system.lib.java import eval_pyjinn_script as eps
import json

bridge = socket.socket()
bridge.bind(("127.0.0.1", 0))
bridge.listen(1)
port = bridge.getsockname()[1]

script = eps(
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
ClickType = JavaClass("net.minecraft.world.inventory.ClickType")
RegistryOps = JavaClass("net.minecraft.resources.RegistryOps")

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

def inventory():
    out = []
    for slot in mc.player.containerMenu.slots:
        itemstack = slot.getItem()
        if str(itemstack) != "0 minecraft:air": out.append(serialize_stack(itemstack))
        else: out.append('{"id":"minecraft:air","count":0}')
    return "[" + ", ".join(out) + "]"

def pickup(slot,mouse):
    slot = int(slot)
    mouse = int(mouse)
    mc.gameMode.handleInventoryMouseClick(mc.player.containerMenu.containerId, slot, mouse, ClickType.PICKUP, mc.player)

def quickmove(slot,mouse):
    slot = int(slot)
    mouse = int(mouse)
    mc.gameMode.handleInventoryMouseClick(mc.player.containerMenu.containerId, slot, mouse, ClickType.QUICKMOVE, mc.player)

def swap(slot1,slot2):
    slot1 = int(slot1)
    slot2 = int(slot2)
    mc.gameMode.handleInventoryMouseClick(mc.player.containerMenu.containerId, slot1, slot2, ClickType.SWAP, mc.player)

def open():
    mc.options.keyInventory.setDown(True)
    mc.options.keyInventory.setDown(False)

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
"get_item":get_item
}

def frame(_):
    try: line = reader.readLine()
    except: return
    if line:
        cmd = line.split(":")
        if cmd[1]: return_call(callables[cmd[0]](*cmd[1].split(",")))
        else: return_call(callables[cmd[0]]())

add_event_listener("render",frame)
""")

conn, _ = bridge.accept()
file = conn.makefile(mode="rw")

def await_function_call(func_name,*args):
    file.write(f"{func_name}:{",".join(args) if args else ""}\n")
    file.flush()
    while True:
        line = file.readline()
        if not line: continue
        else: break
    return line[:-1]

def inventory() -> dict[dict]:
    """
    Returns the entire player inventory, as a dict
    """
    return json.loads(await_function_call("inventory"))

def pickup(slot,mouse=1):
    """
    Simulate a pickup action on a slot
    """
    await_function_call("pickup",str(slot),str(mouse))

def quickmove(slot,mouse):
    """
    Simulate a quickmove action on a slot
    """
    await_function_call("quickmove",str(slot),str(mouse))

def swap(slot1,slot2):
    """
    Simulate a swap action on 2 slots
    """
    await_function_call("swap",str(slot1),str(slot2))

def open():
    """
    Opens up the players inventory
    """
    await_function_call("open")

def get_item(slot) -> dict:
    """
    Get the item from a slot
    """
    return json.loads(await_function_call("get_item",str(slot)))

print(inventory())