import inspect
import json
import socket
from system.lib.java import eval_pyjinn_script as eps
from uuid import uuid4
from concurrent.futures import Future
from threading import Thread
from functools import wraps

concurrent = {}

def as_pyjinn(include={}, event=None, type="noreturn"):
    def decorator(func):
        if not hasattr(func, "Jynnton_id"): func.Jynnton_id = str(uuid4())
        if not hasattr(func, "Jynnton_init"): func.Jynnton_init = True
        @wraps(func)
        def wrapper(*args, **kwargs):
            if func.Jynnton_init:
                kwargs["init"] = True
                func.Jynnton_init = False
            elif "init" not in kwargs: kwargs["init"] = False
            ufcid = str(uuid4())
            data = json.dumps({"code": "\n".join(inspect.getsource(func).split("\n")[1:])[:-1], "includes": include, "event": event, "name": func.__name__, "id": func.Jynnton_id, "type": type, "ufcid": ufcid, "args": args, "init": kwargs["init"]})
            writer.write(data + "\n")
            writer.flush()
            if type == "returning" and not kwargs["init"]:
                response = Future()
                concurrent[ufcid] = response
                resp = response.result()
                concurrent.pop(ufcid)
                if resp["fail"]: raise RuntimeError(resp["result"])
                return resp["result"]
        wrapper()
        return wrapper
    return decorator

bridge = socket.socket()
bridge.bind(("127.0.0.1", 0))
bridge.listen(1)
port = bridge.getsockname()[1]

eps(
r"""
debug_log = False

import pyjinn_json as json
Minescript = JavaClass("net.minescript.common.Minescript")
Script = JavaClass("org.pyjinn.interpreter.Script")
ClassMethodName = JavaClass("org.pyjinn.interpreter.Script$ClassMethodName")
Array = JavaClass("java.lang.reflect.Array")
Object = JavaClass("java.lang.Object")
BufferedWriter = JavaClass("java.io.BufferedWriter")
OutputStreamWriter = JavaClass("java.io.OutputStreamWriter")
Socket = JavaClass("java.net.Socket")
StandardCharsets = JavaClass("java.nio.charset.StandardCharsets")
BufferedReader = JavaClass("java.io.BufferedReader")
InputStreamReader = JavaClass("java.io.InputStreamReader")
Random = JavaClass("java.util.Random")()
ScriptBoundFunction = JavaClass("org.pyjinn.interpreter.Script$BoundFunction")

log("[Jynnton] Waking up ...")
bridge = Socket("127.0.0.1", """ + str(port) + r""")
bridge.setSoTimeout(1)
writer = BufferedWriter(OutputStreamWriter(bridge.getOutputStream(), StandardCharsets.UTF_8))
reader = BufferedReader(InputStreamReader(bridge.getInputStream(), StandardCharsets.UTF_8))
builtin_funcs = ["set_chat_input","player_hand_items","get_block","echo","player_press_drop","player_press_forward","player_press_sneak","getblock","_SleepRequest","__script__","ManagedCallback","player_inventory_select_slot","getblocklist","screen_name","player_name","player_orientation","get_entities","_System","Script","add_event_listener","BlockPacker","player_get_targeted_entity","players","player_press_left","get_player","execute","get_block_region","echo_json","player_press_attack","__name__","set_interval","append_chat_history","player_get_targeted_block","container_get_items","log","job_info","_EventRequest","show_chat_screen","screenshot","sys","player_press_jump","player_press_backward","player_set_orientation","chat_input","player_position","BlockPack","player_press_pick_item","_Coroutine","Minescript","BlockRegion","player","player_press_sprint","player_press_right","remove_event_listener","player_inventory","player_look_at","player_press_swap_hands","version_info","get_players","Rotation","Rotations","get_block_list","combine_rotations","set_timeout","EventLoop","press_key_bind","entities","chat","player_health","_RuntimeException","world_info","player_press_use"]
portid = "Jynnton_globals:" + str(""" + str(port) + r""")
__script__.vars["game"][portid] = {}
__script__.vars["game"][portid]["globals"] = {}
__script__.vars["game"][portid]["funcs"] = []
__script__.vars["game"][portid]["callback"] = {}

common = {
    "mc":'mc = JavaClass("net.minecraft.client.Minecraft").getInstance()',
    "mappings": 'mappings = JavaClass("net.minescript.common.Minescript").mappingsLoader.get()',
    "Gizmos": 'Gizmos = JavaClass("net.minecraft.gizmos.Gizmos")',
    "ARGB": 'ARGB = JavaClass("net.minecraft.util.ARGB")',
    "BlockPos": 'BlockPos = JavaClass("net.minecraft.core.BlockPos")',
    "GizmoStyle": 'GizmoStyle = JavaClass("net.minecraft.gizmos.GizmoStyle")',
    "globals": f'globals = __script__.vars["game"]["{portid}"]["globals"]',
    "invoke": f'def invoke(name,*args): __script__.vars["game"]["{portid}"]["funcs"].append([name,args])'
}

cached_scripts = {}
active_scripts = []

class RuntimeScript:
    def __init__(self,this,namespace,name):
        self.script = this
        self.namespace = namespace
        self.name = name
        active_scripts.append(self)
    
    def invoke(self,func,*args):
        array_args = Array.newInstance(type(Object),len(args))
        for i,arg in enumerate(args):
            Array.set(array_args, i, arg)
        return self.namespace[func].call(self.script.mainModule().globals().env(),array_args)

def map(callable,iterable):
    return [callable(i) for i in iterable]

def reverse(lst):
    out = [None for _ in range(len(lst))]
    i = len(lst)-1
    if i > 0:
        for item in lst:
            out[i] = item
            i -= 1
    else: return lst
    return out

def exec(source, name, expected_names:list=[], tied_event:str=None):
    log("[Jynnton] Creating new script instance")
    classes = []
    for item in expected_names:
        parts = item.split("@")
        key = parts[0]
        value = map(str,parts[1:])
        value = "@".join(value)
        if key == "common": classes.append(common[value]) ; log(f"[Jynnton] Adding common includable: {value}")
        elif key == "special": classes.append(value) ; log(f"[Jynnton] Adding special includable: {value}")
        else: classes.append(f'{value.split(".")[-1]} = JavaClass("{value}")') ; log(f"[Jynnton] Adding class includable: {value}")
    source += "\n" + "\n".join(classes)
    if tied_event: source += f'\nadd_event_listener("{tied_event}",{name})'
    log("[Jynnton] Source code injection complete")
    script = Minescript.loadPyjinnScript(JavaList(["__eval__.pyj"]), source)
    script.redirectStdout(__script__.stdout)
    script.redirectStderr(__script__.stderr)
    for name in __script__.vars.keys():
        script.vars[name] = __script__.vars[name]
    script.atExit(lambda status: __script__.exit(status))
    script.exec()
    log("[Jynnton] Script created from source code")
    out = {}
    for key in script.mainModule().globals().vars():
        if key not in builtin_funcs: out[key] = script.get(key)
    log(f"[Jynnton] Finished script, src: \n{source}")
    return RuntimeScript(script,out,"TEST")

def return_call(data):
    writer.write(json.dumps(data) + "\n")
    writer.flush()

def frame(_):
    lines = []
    iters = 0
    while True:
        iters += 1
        if iters > 50: log("[Jynnton] Overloaded! Exiting reader...") ; break
        try:
            line = reader.readLine()
            if line: lines.append(line)
            else: break
        except Exception as e:
            if "SocketTimeout" not in str(e): log(f"[Jynnton] Exception caught! {e}")
            break
    for line in lines:
        payload = json.loads(line)
        if payload["id"] not in cached_scripts:
            cached_scripts[payload["id"]] = exec(payload["code"],payload["name"],payload["includes"],payload["event"])
            log("[Jynnton] Caching uncached script")
        if not payload["init"]:
            try: result = cached_scripts[payload["id"]].invoke(payload["name"],*payload["args"]) ; fail = False
            except Exception as e: result = str(e) ; fail = True
            if payload["type"] == "returning":
                return_call({"fail":fail,"result":result,"ufcid":payload["ufcid"]})
    for name, args in __script__.vars["game"][portid]["funcs"]:
        if debug_log: log(f"[Jynnton-Debug] Resolving invocation: {name}{args}")
        for script in active_scripts:
            if debug_log: log(f"[Jynnton-Debug] Searching for function in {script.namespace}")
            if name in script.namespace:
                if debug_log: log(f"[Jynnton-Debug] Found name {name}")
                script.invoke(name, *args)
    __script__.vars["game"][portid]["funcs"] = []

log("[Jynnton] Starting main loop")
add_event_listener("render",frame)
""")

conn, _ = bridge.accept()
reader = conn.makefile("r", encoding="utf-8")
writer = conn.makefile("w", encoding="utf-8")

def __reader__():
    while True:
        line = reader.readline()
        data = json.loads(line[:-1])
        if data["ufcid"] in concurrent: concurrent[data["ufcid"]].set_result(data)

Thread(target=__reader__,daemon=True).start()

@as_pyjinn(type="returning",include=["common@globals"])
def snapshot_pyjinn_globals():
    return globals
