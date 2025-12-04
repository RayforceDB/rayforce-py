# :material-clock-fast: Technical Details

### :material-wrench: How Rayforce-Py Operates

Rayforce-Py utilizes the C API to interact with the Rayforce runtime and call Rayforce functions,
which allows it to achieve great performance without practical overhead in query execution time.

Our goal is to expose each useful Rayforce type and function to the Python level and provide
representations to operate with them within the Python runtime.

### :material-memory: How Memory Management Works

Upon import of the Rayforce library, the Rayforce runtime is initiated under the hood.
This runtime has its own memory, which Python accesses through FFI methods.

Python has a high-level representation of a Rayforce pointer called `RayObject`. This object holds
information about the memory address of a specific object. `RayObject` has its own set of untyped
attributes which are called within the FFI module, and it is <b>highly not recommended</b> to access them directly instead of via the library. Accessing and operating with it directly might cause memory and segmentation issues, which we're trying our best to avoid across the library.

```python
# This is Rayforce-Py object, safe to work and operate with
>>> I64(123)
I64(123)

# This is RayObject, which holds information 
# about memory address of the underlying Rayforce object, 
# Not recommended to access and operate with directly,
# unless you know what you're doing :)
>>> I64(123).ptr
<_rayforce_c.RayObject at 0x1095aadb0>

```

Python maintains reference counts for that object, hence Rayforce's GC doesn't remove the object unless
the reference count of that object becomes 0. This mechanism works vice versa - Python also checks for RayObject pointers with a reference count of 0 within the runtime so that the GC can collect the object.
