#include "rayforce_c.h"

PyObject *raypy_update(PyObject *self, PyObject *args) {
  (void)self;
  CHECK_MAIN_THREAD();

  RayObject *update_dict;

  if (!PyArg_ParseTuple(args, "O!", &RayObjectType, &update_dict))
    return NULL;

  obj_p call_args[1] = {update_dict->obj};
  obj_p ray_obj = ray_update(call_args, 1);
  if (ray_obj == NULL) {
    PyErr_SetString(PyExc_RuntimeError,
                    "query: failed to execute update query");
    return NULL;
  }
  /* If ray_obj is RAY_ERROR, wrap & let Python error_handler map code. */
  return raypy_wrap_ray_object(ray_obj);
}
PyObject *raypy_insert(PyObject *self, PyObject *args) {
  (void)self;
  CHECK_MAIN_THREAD();

  RayObject *table_obj;
  RayObject *data_obj;

  if (!PyArg_ParseTuple(args, "O!O!", &RayObjectType, &table_obj,
                        &RayObjectType, &data_obj))
    return NULL;

  obj_p call_args[2] = {table_obj->obj, data_obj->obj};
  obj_p ray_obj = ray_insert(call_args, 2);
  if (ray_obj == NULL) {
    PyErr_SetString(PyExc_RuntimeError,
                    "query: failed to execute insert query");
    return NULL;
  }
  return raypy_wrap_ray_object(ray_obj);
}
PyObject *raypy_upsert(PyObject *self, PyObject *args) {
  (void)self;
  CHECK_MAIN_THREAD();

  RayObject *table_obj;
  RayObject *keys_obj;
  RayObject *data_obj;

  if (!PyArg_ParseTuple(args, "O!O!O!", &RayObjectType, &table_obj,
                        &RayObjectType, &keys_obj, &RayObjectType, &data_obj))
    return NULL;

  obj_p call_args[3] = {table_obj->obj, keys_obj->obj, data_obj->obj};
  obj_p ray_obj = ray_upsert(call_args, 3);
  if (ray_obj == NULL) {
    PyErr_SetString(PyExc_RuntimeError,
                    "query: failed to execute upsert query");
    return NULL;
  }
  return raypy_wrap_ray_object(ray_obj);
}
