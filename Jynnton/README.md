# Jynnton - Pyjinn from Python
Jynnton (`ˈdʒɪn.θən`, aka Jinn-ton) is a library made for Minescript, that allows you to create and run Pyjinn functions from Python.

Requirements:
- Minescript 5.0+
- Mappings (`\install_mappings`) for versions below 26.x
- `pyjinn_json`: https://github.com/SmartBoty/Minescript/blob/main/pyjinn/pyjinn_json.py
- Only tested on version 1.21.11, but may work on other versions aswell
- Python 3.12 +

What this library allows you to do:
- Execute Pyjinn code, straight from Python
- Easy calback between Python and Pyjinn
- Run functions on Pyjinn events
- And ofc, access java internals in just miliseconds

## How to use the library
Very simple actually. Just use the given decorator
```py
from Jynnton import as_pyjinn

@as_pyjinn()
def foo(): pass
```
Upon calling `foo()`, the function will now be called in Pyjinn

Example usage:
```py
from Jynnton import as_pyjinn, register_python_function, add_event_listener, JynntonFlags
from pynput.mouse import Controller
from time import sleep
mouse = Controller()

# make sure all of these JynntonFlags are on one line ↓↓↓
@as_pyjinn(JynntonFlags.JavaClass("net.minecraft.gizmos.Gizmos"), JynntonFlags.JavaClass("net.minecraft.util.ARGB"), JynntonFlags.JavaClass("net.minecraft.core.BlockPos"), JynntonFlags.JavaClass("net.minecraft.gizmos.GizmoStyle"))
def render(event):
    Gizmos.cuboid(BlockPos(0,0,0),GizmoStyle.stroke(ARGB.color(255,200,100,200)))

@as_pyjinn()
async def tick(event):
    x,y = await get_mouse_position() # when calling out to python functions, always use 'await', otherwise it will silently fail
    print(f"X: {x}, Y: {y}")

@register_python_function
def get_mouse_position():
    return mouse.position

add_event_listener("render",render)
add_event_listener("tick",tick)

while True: sleep(1) # Keep the script alive
```

This will render a cube at the block you are looking at
```
from Jynnton import as_pyjinn, add_event_listener, JynntonFlags
from time import sleep

@as_pyjinn(JynntonFlags.mc,JynntonFlags.JavaClass("net.minecraft.world.phys.BlockHitResult"),JynntonFlags.JavaClass("net.minecraft.gizmos.Gizmos"), JynntonFlags.JavaClass("net.minecraft.util.ARGB"), JynntonFlags.JavaClass("net.minecraft.core.BlockPos"), JynntonFlags.JavaClass("net.minecraft.gizmos.GizmoStyle") )
def render(event):
    hit = mc.hitResult
    if hit:
        if hit.getType() == BlockHitResult.Type.BLOCK:
            Gizmos.cuboid(BlockPos(hit.getBlockPos()),GizmoStyle.stroke(ARGB.color(255,200,100,200))).setAlwaysOnTop()
add_event_listener("render",render)

while True: sleep(1) 
```
