#!python
from system.pyj.minescript import *

TYPE_CHECKING = True
TYPE_CHECKING = not TYPE_CHECKING

_System = JavaClass("java.lang.System")
_Gson = JavaClass("com.google.gson.GsonBuilder")().serializeNulls().create()
_Map = JavaClass("java.util.Map")
_HashMap = JavaClass("java.util.HashMap")
_List = JavaClass("java.util.List")
_ArrayList = JavaClass("java.util.ArrayList")
_Files = JavaClass("java.nio.file.Files")
_Paths = JavaClass("java.nio.file.Paths")
_Path = JavaClass("java.nio.file.Path")
_FileAlreadyExistsException = JavaClass("java.nio.file.FileAlreadyExistsException")
_NoSuchFileException = JavaClass("java.nio.file.NoSuchFileException")
_Array = JavaClass("java.lang.reflect.Array")
_Object = JavaClass("java.lang.Object")
_String = JavaClass("java.lang.String")
_LinkOption = JavaClass("java.nio.file.LinkOption")
_FileAttribute = JavaClass("java.nio.file.attribute.FileAttribute")
_Random = JavaClass("java.util.Random")()
_Math = JavaClass("java.lang.Math")
_Thread = JavaClass("java.lang.Thread")
_Runnable = JavaClass("java.lang.Runnable")
_mappings = JavaClass("net.minescript.common.Minescript").mappingsLoader.get()

class Platform:
    def __init__(self):
        self._os = _System.getProperty("os.name").toLowerCase()
    
    def get_os(self):
        return Platform._os

Platform = Platform()

class Utils:
    def as_java_list(self,items):
        lst = _ArrayList()
        for item in items:
            lst.add(item)
        return _List.copyOf(lst)

    def isdigit(self,item):
        if isinstance(item,(int,float)): return True
        if item.startswith("-"): item = item[1:]
        try: float(item) ; return True
        except: pass
        return False

    def as_array(self,items,specific_type=_Object):
        array = _Array.newInstance(type(specific_type),len(items))
        for i,item in enumerate(items):
            _Array.set(array, i, item)
        return array
    
    def map(self,callable,iterable):
        return [callable(i) for i in iterable]
    
    def reflect_field(self, _class, field_name, raw=False):
        clss = _class.getClass()
        f = _mappings.getRuntimeFieldName(clss, field_name)
        field = clss.getDeclaredField(f)
        field.setAccessible(True)
        if not raw: return field.get(_class)
        else: return field
    
    def reflect_method(self, _class, method_name, raw=False):
        prettyname = method_name
        try:
            methods = type(_class).getDeclaredMethods()
            method_name = _mappings.getRuntimeMethodNames(type(_class),method_name).asList()[0]
        except:
            methods = _class.getClass().getDeclaredMethods()
            method_name = _mappings.getRuntimeMethodNames(_class.getClass(),method_name).asList()[0]
        set = False
        reflected_methods = []
        for method in methods:
            if method.getName() == method_name:
                method.setAccessible(True)
                set = True
                reflected_methods.append(method)
        if not set: raise _RuntimeException(f"Method '{prettyname}' doesnt exist on '{_class}'")
        if raw: return reflected_methods
        else: return [lambda *args: method.invoke(_class, *args) for method in reflected_methods]

Utils = Utils()

class json:
    def mapify_pyjinndict(self,pyjinndict):
        out = _HashMap()
        for key,value in pyjinndict.items():
            if isinstance(value,dict): v = json.mapify_pyjinndict(value)
            else: v = value
            out.put(key,v)
        return out

    def dictify_javamap(self,javamap):
        out = {}
        for key in javamap.keySet():
            typ = str(type(javamap[key]))
            if typ == 'JavaClass("com.google.gson.internal.LinkedTreeMap")': out[key] = json.dictify_javamap(javamap[key])
            else: out[key] = javamap[key]
        return out

    def handle_fromjson(self,obj):
        typ = str(type(obj))
        if typ == 'JavaClass("com.google.gson.internal.LinkedTreeMap")': return json.dictify_javamap(obj)
        elif typ == 'JavaClass("java.util.List")': return Utils.as_java_list([json.handle_fromjson(javaobj) for javaobj in obj])
        else: return obj

    def handle_tojson(self,obj):
        if isinstance(obj, dict): return json.mapify_pyjinndict(obj)
        elif isinstance(obj, list): return Utils.as_java_list([json.handle_tojson(javaobj) for javaobj in obj])
        else: return obj

    def loads(self,s:str):
        if s.strip().startswith("["): return json.handle_fromjson(_Gson.fromJson(s, type(_List)))
        elif s.strip().startswith("{"): return json.handle_fromjson(_Gson.fromJson(s, type(_Map)))
        elif s.strip().startswith("null"): return None
        elif Utils.isdigit(s.strip()): return float(s)
        else: return s

    def dumps(self,obj):
        return _Gson.toJson(json.handle_tojson(obj))

json = json()

class Path:
    def __init__(self,*path):
        self._path_separator = "\\" if "windows" in Platform._os else "/"
        self.path = _Path.of(self._path_separator.join(path), Utils.as_array([],specific_type=_String))

    def exists(self): return _Files.exists(self.path,Utils.as_array([],specific_type=_LinkOption))

    def is_dir(self): return _Files.isDirectory(self.path,Utils.as_array([],specific_type=_LinkOption))

    def is_file(self): return _Files.isRegularFile(self.path,Utils.as_array([],specific_type=_LinkOption))

    def touch(self,exist_ok:bool=False):
        if exist_ok:
            try: _Files.createFile(self.path)
            except _FileAlreadyExistsException: pass
        else: _Files.createFile(self.path)

    def mkdir(self):
        arr = Utils.as_array([],specific_type=_FileAttribute)
        if self.is_file(): _Files.createDirectories(self.path.getParent(),arr)
        else: _Files.createDirectories(self.path,arr)
    
    def unlink(self,missing_ok:bool=False):
        if missing_ok:
            try: _Files.delete(self.path)
            except _NoSuchFileException: pass
        else: _Files.delete(self.path)
    
    def parent(self):
        parent = self.path.getParent()
        if parent: return Path(*str(parent).split(self._path_separator))
        else: return None

    def as_string(self): return str(self.path)

    def as_java_path(self): return self.path

    def __truediv__(self, other):
        if isinstance(other,str): return Path(self.as_string(),other)
        elif isinstance(other,Path): return Path(self.as_string(),other.as_string())
        else: raise _RuntimeException(f"Cannot join {type(other)} to Path object")

class time:
    def time(self): return _System.currentTimeMillis()/1000

    def sleep(self,amount): _Thread.sleep(int(amount*1000))

time = time()

class math:
    pi = _Math.PI
    tau = 2*_Math.PI
    e = _Math.E
    def abs(self,num): return _Math.abs(num)
    def floor(self, num): return _Math.floor(num)
    def ceil(self, num): return _Math.ceil(num)
    def sqrt(self, num): return _Math.sqrt(num)
    def pow(self, num, power): return _Math.pow(num,power)
    def sin(self, num): return _Math.sin(num)
    def cos(self, num): return _Math.cos(num)
    def tan(self, num): return _Math.tan(num)
    def asin(self, num): return _Math.asin(num)
    def acos(self, num): return _Math.acos(num)
    def atan(self, num): return _Math.atan(num)
    def atan2(self, num, theta): return _Math.atan2(num, theta)
    def radians(self, num): return _Math.toRadians(num)
    def degrees(self, num): return _Math.toDegrees(num)
    def hypot(self, x, y): return _Math.hypot(x,y)
    def sign(self, num): return _Math.signum(num)

math = math()

class random:
    def random(self): return _Random.nextFloat()

    def randint(self,lower=0,upper=1): 
        if upper < lower: raise _RuntimeException("Lower bound larger than upper bound!")
        return _Random.nextInt(upper-lower+1) + lower

    def choice(self,iterable):
        if isinstance(iterable,dict): return iterable.keys()[random.randint(upper=len(iterable)-1)]
        else: return iterable[random.randint(upper=len(iterable)-1)]

random = random()

class Thread:
    def __init__(self,target,daemon=None):
        self.thread = _Thread(_Runnable(target))
        self.thread.setDaemon(daemon)
    
    def start(self):
        self.thread.start()

    def stop(self):
        self.thread.stop()



if TYPE_CHECKING:
    class _RuntimeException(Exception): pass
    class Platform:
        @staticmethod
        def get_os() -> str:
            """
            Get the current OS
            """
    class Utils:
        @staticmethod
        def as_java_list(items:list|tuple):
            """
            Convert an iterable to a Java list
            """
        @staticmethod
        def isdigit(item:str) -> bool:
            """
            Returns `True` if items is a digit
            """
        @staticmethod
        def as_array(items,specific_type=_Object):
            """
            Convert an iterable to a Java Array
            
            Optionally specify a type
            """
        @staticmethod
        def map(callable,iterable:list|tuple) -> list:
            """
            Calls `callable` with every item in `iterable`, and returns each in a list
            """
        @staticmethod
        def reflect_field(_class, field_name:str, raw:bool=False):
            """
            Returns a fields value, regardless if its visible or not.

            If `raw` is `True`, it returns the field itself, rather than its value
            """
        @staticmethod
        def reflect_method(_class, method_name, raw:bool=True) -> list:
            """
            Returns a list of callables, of all methods matching the method name, regardless of visibility

            If `raw` is `True`, it returns the methods themselves, rather than a wrapper lambda
            """
    
    class json:
        """
        Recreation of the `json` library for Pyjinn
        """
        @staticmethod
        def loads(json_string:str):
            """
            Converts Json-string into a Python (Pyjinn) object
            """
        @staticmethod
        def dumps(obj) -> str:
            """
            Converts a Python (Pyjinn) object into Json-string
            """
    
    class Path:
        """
        Recreation of the `Path` class from `pathlib` for Pyjinn

        Supports concatenation of Path with str:
        `Path("foo") / bar` -> `"foo/bar"` (or `"foo\\bar"`, depending on OS)
        """
        def __init__(self,*path_parts): pass
        def exists(self) -> bool:
            """
            Returns `True` if the path exists as a file or directory
            """
        def is_dir(self) -> bool:
            """
            Returns `True` if the path exists as a directory
            """
        def is_file(self) -> bool:
            """
            Returns `True` if the path exists as a file
            """
        def touch(self,exist_ok:bool=False):
            """
            Creates a file
            """
        def mkdir(self):
            """
            Creates directories if they dont exist
            """
        def unlink(self,missing_ok:bool=False):
            """
            Deletes a file or directory
            """
        def parent(self) -> Path:
            """
            Gets the parent from the path
            """
        def as_string(self) -> str:
            """
            Returns the path as a string
            """
        def as_java_path(self):
            """
            Returns the path as a Java Path
            """
    
    class time:
        @staticmethod
        def time() -> float:
            """
            Returns the current system time as a float
            """
        @staticmethod
        def sleep(amount:float):
            """
            Blocks the current Thread for a set amount of seconds

            Note: Freezes the game if ran on the main thread
            """
    
    class math:
        """
        Recreation of the `math` library for Pyjinn
        """
        pi = _Math.PI
        tau = 2*_Math.PI
        e = _Math.E
        @staticmethod
        def abs(num) -> float: pass
        @staticmethod
        def floor(num) -> float: pass
        @staticmethod
        def ceil(num) -> float: pass
        @staticmethod
        def sqrt(num) -> float: pass
        @staticmethod
        def pow(num, power) -> float: pass
        @staticmethod
        def sin(num) -> float: pass
        @staticmethod
        def cos(num) -> float: pass
        @staticmethod
        def tan(num) -> float: pass
        @staticmethod
        def asin(num) -> float: pass
        @staticmethod
        def acos(num) -> float: pass
        @staticmethod
        def atan(num) -> float: pass
        @staticmethod
        def atan2(num, theta) -> float: pass
        @staticmethod
        def radians(num) -> float: pass
        @staticmethod
        def degrees(num) -> float: pass
        @staticmethod
        def hypot(x, y) -> float: pass
        @staticmethod
        def sign(num) -> float: pass
    
    class random:
        """
        Recreation of the `random` library for Pyjinn
        """
        @staticmethod
        def random() -> float:
            """
            Returns a float between 0 - 1
            """
        @staticmethod
        def randint(lower=0,upper=1) -> int:
            """
            Returns a random integer between the specified range
            """
        @staticmethod
        def choice(iterable):
            """
            Randomly chooses an item from the iterable
            """
    
    class Thread:
        """
        Recreation of the `Thread` class from `threading` for Pyjinn
        """
        def __init__(self,target,daemon=None): pass
        def start(self):
            """
            Start the Thread
            """
        def stop(self):
            """
            Stop the Thread
            """
