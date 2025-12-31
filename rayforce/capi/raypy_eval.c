#include "rayforce_c.h"

PyObject *raypy_eval_str(PyObject *self, PyObject *args) {
  (void)self;
  CHECK_MAIN_THREAD();
  RayObject *item;

  if (!PyArg_ParseTuple(args, "O!", &RayObjectType, &item))
    return NULL;

  obj_p ray_obj = ray_eval_str(item->obj, NULL_OBJ);
  if (ray_obj == NULL) {
    PyErr_SetString(PyExc_RuntimeError, "Failed to evaluate expression");
    return NULL;
  }
  return raypy_wrap_ray_object(ray_obj);
}
PyObject *raypy_eval_obj(PyObject *self, PyObject *args) {
  (void)self;
  CHECK_MAIN_THREAD();
  RayObject *item;

  if (!PyArg_ParseTuple(args, "O!", &RayObjectType, &item))
    return NULL;

  obj_p ray_obj = eval_obj(item->obj);
  if (ray_obj == NULL) {
    PyErr_SetString(PyExc_RuntimeError, "Failed to evaluate expression");
    return NULL;
  }
  return raypy_wrap_ray_object(ray_obj);
}
