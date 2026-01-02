#include "rayforce_c.h"

PyObject *raypy_binary_set(PyObject *self, PyObject *args) {
  (void)self;
  CHECK_MAIN_THREAD();
  RayObject *symbol_or_path;
  RayObject *value;

  if (!PyArg_ParseTuple(args, "O!O!", &RayObjectType, &symbol_or_path,
                        &RayObjectType, &value))
    return NULL;

  if (symbol_or_path->obj->type != -TYPE_SYMBOL &&
      symbol_or_path->obj->type != TYPE_C8) {
    PyErr_SetString(PyExc_RuntimeError,
                    "binary: first argument must be a symbol or string");
    return NULL;
  }

  obj_p ray_obj = binary_set(symbol_or_path->obj, value->obj);
  if (ray_obj == NULL) {
    PyErr_SetString(PyExc_RuntimeError, "binary: failed to set value");
    return NULL;
  }
  return raypy_wrap_ray_object(ray_obj);
}
PyObject *raypy_set_obj_attrs(PyObject *self, PyObject *args) {
  (void)self;
  CHECK_MAIN_THREAD();
  RayObject *ray_obj;
  long value;

  if (!PyArg_ParseTuple(args, "O!l", &RayObjectType, &ray_obj, &value))
    return NULL;

  ray_obj->obj->attrs = (char)value;
  Py_RETURN_NONE;
}
PyObject *raypy_quote(PyObject *self, PyObject *args) {
  (void)self;
  CHECK_MAIN_THREAD();
  RayObject *item;

  if (!PyArg_ParseTuple(args, "O!", &RayObjectType, &item))
    return NULL;

  obj_p ray_obj = ray_quote(item->obj);
  if (ray_obj == NULL) {
    PyErr_SetString(PyExc_RuntimeError, "binary: failed to quote object");
    return NULL;
  }
  return raypy_wrap_ray_object(ray_obj);
}
