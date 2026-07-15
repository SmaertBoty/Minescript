#!python
from system.pyj.minescript import JavaClass # juicy syntax coloring

Gson = JavaClass("com.google.gson.GsonBuilder")().serializeNulls().create()
Map = JavaClass("java.util.Map")
HashMap = JavaClass("java.util.HashMap")
List = JavaClass("java.util.List")
ArrayList = JavaClass("java.util.ArrayList")

def listify(*args):
    lst = ArrayList()
    for arg in args:
        lst.add(arg)
    return List.copyOf(lst)

def isdigit(item):
    if item.startswith("-"): item = item[1:]
    try: float(item) ; return True
    except: pass
    return False

def mapify_pyjinndict(pyjinndict):
    out = HashMap()
    for key,value in pyjinndict.items():
        if isinstance(value,dict): v = mapify_pyjinndict(value)
        elif isinstance(value, list): v =  listify(*[handle_tojson(javaobj) for javaobj in value])
        else: v = value
        out.put(key,v)
    return out

def dictify_javamap(javamap):
    out = {}
    for key in javamap.keySet():
        typ = str(type(javamap[key]))
        if typ == 'JavaClass("com.google.gson.internal.LinkedTreeMap")': out[key] = dictify_javamap(javamap[key])
        else: out[key] = javamap[key]
    return out

def handle_fromjson(obj):
    typ = str(type(obj))
    if typ == 'JavaClass("com.google.gson.internal.LinkedTreeMap")': return dictify_javamap(obj)
    elif typ == 'JavaClass("java.util.List")': return listify(*[handle_fromjson(javaobj) for javaobj in obj])
    else: return obj

def handle_tojson(obj):
    if isinstance(obj, dict): return mapify_pyjinndict(obj)
    elif isinstance(obj, (list,tuple)): return listify(*[handle_tojson(javaobj) for javaobj in obj])
    else: return obj

def loads(s:str):
    if s.strip().startswith("["): return handle_fromjson(Gson.fromJson(s, type(List)))
    elif s.strip().startswith("{"): return handle_fromjson(Gson.fromJson(s, type(Map)))
    elif s.strip().startswith("null"): return None
    elif isdigit(s.strip()): return float(s)
    else: return s

def dumps(obj):
    return Gson.toJson(handle_tojson(obj))