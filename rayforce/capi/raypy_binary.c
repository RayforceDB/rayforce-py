#include "rayforce_c.h"

PyObject *raypy_binary_set(PyObject *self, PyObject *args) {
  (void)self;
  CHECK_MAIN_THREAD();
  RayObject *symbol_or_path;
  RayObject *value;

  if (!PyArg_ParseTuple(args, "O!O!", &RayObjectType, &symbol_or_path,
                        &RayObjectType, &value))
    return NULL;

  ray_t *target = symbol_or_path->obj;

  if (target->type == -RAY_SYM) {
    if (ray_env_set(target->i64, value->obj) != RAY_OK) {
      PyErr_SetString(PyExc_RuntimeError, "binary: failed to set env binding");
      return NULL;
    }
    ray_retain(value->obj);
    return raypy_wrap_ray_object(value->obj);
  }

  if (target->type == -RAY_STR) {
    const char *path = ray_str_ptr(target);
    if (ray_obj_save(value->obj, path) != RAY_OK) {
      PyErr_Format(PyExc_RuntimeError, "binary: failed to save object to '%s'",
                   path);
      return NULL;
    }
    ray_retain(value->obj);
    return raypy_wrap_ray_object(value->obj);
  }

  PyErr_SetString(PyExc_RuntimeError,
                  "binary: first argument must be a symbol or string");
  return NULL;
}
PyObject *raypy_set_obj_attrs(PyObject *self, PyObject *args) {
  (void)self;
  CHECK_MAIN_THREAD();
  RayObject *ray_obj;
  long value;

  if (!PyArg_ParseTuple(args, "O!l", &RayObjectType, &ray_obj, &value))
    return NULL;

  ray_obj->obj->attrs = (uint8_t)value;
  Py_RETURN_NONE;
}
PyObject *raypy_quote(PyObject *self, PyObject *args) {
  (void)self;
  CHECK_MAIN_THREAD();
  RayObject *item;

  if (!PyArg_ParseTuple(args, "O!", &RayObjectType, &item))
    return NULL;

  if (item->obj == NULL) {
    PyErr_SetString(PyExc_RuntimeError, "binary: cannot quote null object");
    return NULL;
  }
  ray_retain(item->obj);
  return raypy_wrap_ray_object(item->obj);
}
