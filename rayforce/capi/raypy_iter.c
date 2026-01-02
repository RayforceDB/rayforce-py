#include "rayforce_c.h"

PyObject *raypy_insert_obj(PyObject *self, PyObject *args) {
  (void)self;
  CHECK_MAIN_THREAD();
  RayObject *ray_obj;
  Py_ssize_t index;
  RayObject *item;

  if (!PyArg_ParseTuple(args, "O!nO!", &RayObjectType, &ray_obj, &index,
                        &RayObjectType, &item))
    return NULL;

  if (ins_obj(&ray_obj->obj, (i64_t)index, clone_obj(item->obj)) == NULL) {
    PyErr_SetString(PyExc_RuntimeError,
                    "iter: failed to insert object at index");
    return NULL;
  }
  Py_RETURN_NONE;
}
PyObject *raypy_push_obj(PyObject *self, PyObject *args) {
  (void)self;
  CHECK_MAIN_THREAD();

  RayObject *ray_obj;
  RayObject *item;

  if (!PyArg_ParseTuple(args, "O!O!", &RayObjectType, &ray_obj, &RayObjectType,
                        &item))
    return NULL;

  if (push_obj(&ray_obj->obj, clone_obj(item->obj)) == NULL) {
    PyErr_SetString(PyExc_RuntimeError, "iter: failed to push object");
    return NULL;
  }
  Py_RETURN_NONE;
}
PyObject *raypy_set_obj(PyObject *self, PyObject *args) {
  (void)self;
  CHECK_MAIN_THREAD();

  RayObject *ray_obj;
  RayObject *idx_obj;
  RayObject *val_obj;

  if (!PyArg_ParseTuple(args, "O!O!O!", &RayObjectType, &ray_obj,
                        &RayObjectType, &idx_obj, &RayObjectType, &val_obj))
    return NULL;

  if (set_obj(&ray_obj->obj, idx_obj->obj, clone_obj(val_obj->obj)) == NULL) {
    PyErr_SetString(PyExc_RuntimeError, "iter: failed to set object at index");
    return NULL;
  }
  Py_RETURN_NONE;
}
