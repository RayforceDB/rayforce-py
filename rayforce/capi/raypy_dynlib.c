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

  obj_p path_obj = vector(TYPE_C8, path_len);
  if (path_obj == NULL) {
    PyErr_SetString(PyExc_MemoryError, "Failed to allocate path object");
    return NULL;
  }
  memcpy(AS_C8(path_obj), path, path_len);

  obj_p func_obj = vector(TYPE_C8, func_len);
  if (func_obj == NULL) {
    drop_obj(path_obj);
    PyErr_SetString(PyExc_MemoryError, "Failed to allocate fn name object");
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

  obj_p ray_obj = ray_loadfn((obj_p[]){path_obj, func_obj, nargs_obj}, 3);
  drop_obj(path_obj);
  drop_obj(func_obj);
  drop_obj(nargs_obj);

  if (ray_obj == NULL) {
    PyErr_SetString(PyExc_RuntimeError, "Failed load fn from shared library");
    return NULL;
  }
  return raypy_wrap_ray_object(ray_obj);
}
