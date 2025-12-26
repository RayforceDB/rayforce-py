#include "rayforce_c.h"

PyObject *raypy_select(PyObject *self, PyObject *args) {
  (void)self;
  RayObject *query_dict;

  if (!PyArg_ParseTuple(args, "O!", &RayObjectType, &query_dict))
    return NULL;

  RayObject *result = (RayObject *)RayObjectType.tp_alloc(&RayObjectType, 0);
  if (result == NULL)
    return NULL;

  result->obj = eval_obj(ray_select(query_dict->obj));
  if (result->obj == NULL) {
    Py_DECREF(result);
    PyErr_SetString(PyExc_RuntimeError, "Failed to execute select query");
    return NULL;
  }

  return (PyObject *)result;
}
PyObject *raypy_update(PyObject *self, PyObject *args) {
  (void)self;
  RayObject *update_dict;

  if (!PyArg_ParseTuple(args, "O!", &RayObjectType, &update_dict))
    return NULL;

  RayObject *result = (RayObject *)RayObjectType.tp_alloc(&RayObjectType, 0);
  if (result == NULL)
    return NULL;

  result->obj = eval_obj(ray_update(update_dict->obj));
  if (result->obj == NULL) {
    Py_DECREF(result);
    PyErr_SetString(PyExc_RuntimeError, "Failed to execute update query");
    return NULL;
  }

  return (PyObject *)result;
}

PyObject *raypy_insert(PyObject *self, PyObject *args) {
  (void)self;
  RayObject *table_obj;
  RayObject *data_obj;

  if (!PyArg_ParseTuple(args, "O!O!", &RayObjectType, &table_obj,
                        &RayObjectType, &data_obj))
    return NULL;

  RayObject *result = (RayObject *)RayObjectType.tp_alloc(&RayObjectType, 0);
  if (result == NULL)
    return NULL;

  obj_p ray_args[2] = {table_obj->obj, data_obj->obj};
  result->obj = eval_obj(ray_insert(ray_args, 2));
  if (result->obj == NULL) {
    Py_DECREF(result);
    PyErr_SetString(PyExc_RuntimeError, "Failed to execute insert");
    return NULL;
  }

  return (PyObject *)result;
}

PyObject *raypy_upsert(PyObject *self, PyObject *args) {
  (void)self;
  RayObject *table_obj;
  RayObject *keys_obj;
  RayObject *data_obj;

  if (!PyArg_ParseTuple(args, "O!O!O!", &RayObjectType, &table_obj,
                        &RayObjectType, &keys_obj, &RayObjectType, &data_obj))
    return NULL;

  RayObject *result = (RayObject *)RayObjectType.tp_alloc(&RayObjectType, 0);
  if (result == NULL)
    return NULL;

  obj_p ray_args[3] = {table_obj->obj, keys_obj->obj, data_obj->obj};
  result->obj = eval_obj(ray_upsert(ray_args, 3));
  if (result->obj == NULL) {
    Py_DECREF(result);
    PyErr_SetString(PyExc_RuntimeError, "Failed to execute upsert");
    return NULL;
  }

  return (PyObject *)result;
}
