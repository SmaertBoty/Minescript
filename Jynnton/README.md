# Jynnton - Pyjinn from Python
Jynnton (`ˈdʒɪn.θən`, aka Jinn-ton) is a library made for Minescript, that allows you to create and run Pyjinn functions from Python.

Requirements:
- Minescript 5.0+
- Mappings (`\install_mappings`) for versions below 26.x
- `pyjinn_json`: https://github.com/SmaertBoty/Minescript/blob/main/pyjinn/pyjinn_json.py
- Only tested on version 1.21.11, but may work on other versions aswell

What this library allows you to do:
- Execute Pyjinn code, straight from Python
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

## Decorator flags
The decorator also allows you to attach special metadata to the function
### Include flags
These specify what java classes your function requires:
#### Common:
- These are builtin, commonly used classes. Inlude them using `"common@ClassName"`
- Possible classes:
  - `mc` -> `net.minecraft.client.Minecraft.getInstance()`
  - `mappings` -> `net.minescript.common.Minescript.mappingsLoader.get()`
  - `Gizmos` -> `net.minecraft.gizmos.Gizmos`
  - `GizmoStyle` -> `net.minecraft.gizmos.GizmoStyle`
  - `ARGB` -> `net.minecraft.util.ARGB`
  - `BlockPos` -> `net.minecraft.core.BlockPos`
#### Class:
- These are your extra classes that your function needs. Include them with `class@class.full.path`
#### Special:
- These are special lines of code, that get executed upon creating the function. Include them with `special@code_snippet`
### Event flag
- Specify an event that will call the function. Use it with `event="event_name"`
- Possible events are all builtin Pyjinn events
### Return flag
- Specify wheter this function returns a piece of data. Use it with `type="returning" / "noreturn"`
- Possible flags:
  - `noreturn` (default)
  - `returning`

Example usage of decorator flags:
- A function that uses common flags, and the render event to render a cube at 0,0,0
```py
from Jynnton import as_pyjinn

@as_pyjinn(include=["common@Gizmos","common@ARGB","common@BlockPos","common@GizmoStyle"],event="render")
def test(_):
    Gizmos.cuboid(BlockPos(0,0,0),GizmoStyle.stroke(ARGB.color(255,200,100,200)))

while True: pass # Keep the script alive
```
