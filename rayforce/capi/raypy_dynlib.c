#include "rayforce_c.h"

PyObject *raypy_loadfn(PyObject *self, PyObject *args) {
  (void)self;
  CHECK_MAIN_THREAD();
  const char *path;
  const char *func_name;
  int nargs;
  Py_ssize_t path_len, func_len;

  if (!PyArg_ParseTuple(args, "s#s#i", &path, &path_len, &func_name, &func_len,
                        &nargs))
    return NULL;

  // Create raw obj_p objects without Python wrappers to avoid use-after-free
  obj_p path_obj = vector(TYPE_C8, path_len);
  if (path_obj == NULL) {
    PyErr_SetString(PyExc_MemoryError, "Failed to allocate path object");
    return NULL;
  }
  memcpy(AS_C8(path_obj), path, path_len);

  obj_p func_obj = vector(TYPE_C8, func_len);
  if (func_obj == NULL) {
    drop_obj(path_obj);
    PyErr_SetString(PyExc_MemoryError,
                    "Failed to allocate function name object");
    return NULL;
  }
  memcpy(AS_C8(func_obj), func_name, func_len);

  obj_p nargs_obj = i64((long long)nargs);
  if (nargs_obj == NULL) {
    drop_obj(path_obj);
    drop_obj(func_obj);
    PyErr_SetString(PyExc_MemoryError, "Failed to allocate nargs object");
    return NULL;
  }

  RayObject *result = (RayObject *)RayObjectType.tp_alloc(&RayObjectType, 0);
  if (result == NULL) {
    drop_obj(path_obj);
    drop_obj(func_obj);
    drop_obj(nargs_obj);
    return NULL;
  }

  obj_p args_array[3];
  args_array[0] = path_obj;
  args_array[1] = func_obj;
  args_array[2] = nargs_obj;

  result->obj = ray_loadfn(args_array, 3);

  // Clean up temporary objects - ray_loadfn clones what it needs
  drop_obj(path_obj);
  drop_obj(func_obj);
  drop_obj(nargs_obj);

  if (result->obj == NULL) {
    Py_DECREF(result);
    PyErr_SetString(PyExc_RuntimeError,
                    "Failed to load function from shared library");
    return NULL;
  }

  return (PyObject *)result;
}
