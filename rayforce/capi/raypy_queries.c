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

/* (read-csv [schema] path) — forward to ray_read_csv_fn. If schema_obj is
 * None, call with just path. Schema must be a RAY_SYM vector of UPPERCASE
 * type names ("I64", "F64", "B8", "DATE", "TIME", "TIMESTAMP", "SYMBOL",
 * "STR", "GUID", "I32", "I16", "U8"). */
PyObject *raypy_read_csv(PyObject *self, PyObject *args) {
  (void)self;
  CHECK_MAIN_THREAD();

  PyObject *schema_arg;
  RayObject *path_obj;

  if (!PyArg_ParseTuple(args, "OO!", &schema_arg, &RayObjectType, &path_obj))
    return NULL;

  obj_p ray_obj;
  if (schema_arg == Py_None) {
    obj_p call_args[1] = {path_obj->obj};
    ray_obj = ray_read_csv_fn(call_args, 1);
  } else {
    if (!PyObject_TypeCheck(schema_arg, &RayObjectType)) {
      PyErr_SetString(PyExc_TypeError,
                      "read_csv: schema must be None or RayObject");
      return NULL;
    }
    obj_p call_args[2] = {((RayObject *)schema_arg)->obj, path_obj->obj};
    ray_obj = ray_read_csv_fn(call_args, 2);
  }

  if (ray_obj == NULL) {
    PyErr_SetString(PyExc_RuntimeError, "read_csv: failed to read CSV");
    return NULL;
  }
  return raypy_wrap_ray_object(ray_obj);
}

/* (write-csv table path) — forward to ray_write_csv_fn. */
PyObject *raypy_write_csv(PyObject *self, PyObject *args) {
  (void)self;
  CHECK_MAIN_THREAD();

  RayObject *table_obj;
  RayObject *path_obj;

  if (!PyArg_ParseTuple(args, "O!O!", &RayObjectType, &table_obj,
                        &RayObjectType, &path_obj))
    return NULL;

  obj_p call_args[2] = {table_obj->obj, path_obj->obj};
  obj_p ray_obj = ray_write_csv_fn(call_args, 2);
  if (ray_obj == NULL) {
    PyErr_SetString(PyExc_RuntimeError, "write_csv: failed to write CSV");
    return NULL;
  }
  return raypy_wrap_ray_object(ray_obj);
}

/* (set-splayed dir table [sym_path]) — forward to ray_set_splayed_fn. If
 * sym_arg is None, the core picks a default sym path; otherwise it must be a
 * STR RayObject. */
PyObject *raypy_set_splayed(PyObject *self, PyObject *args) {
  (void)self;
  CHECK_MAIN_THREAD();

  RayObject *dir_obj;
  RayObject *table_obj;
  PyObject *sym_arg;

  if (!PyArg_ParseTuple(args, "O!O!O", &RayObjectType, &dir_obj, &RayObjectType,
                        &table_obj, &sym_arg))
    return NULL;

  obj_p ray_obj;
  if (sym_arg == Py_None) {
    obj_p call_args[2] = {dir_obj->obj, table_obj->obj};
    ray_obj = ray_set_splayed_fn(call_args, 2);
  } else {
    if (!PyObject_TypeCheck(sym_arg, &RayObjectType)) {
      PyErr_SetString(PyExc_TypeError,
                      "set_splayed: sym_path must be None or RayObject");
      return NULL;
    }
    obj_p call_args[3] = {dir_obj->obj, table_obj->obj,
                          ((RayObject *)sym_arg)->obj};
    ray_obj = ray_set_splayed_fn(call_args, 3);
  }

  if (ray_obj == NULL) {
    PyErr_SetString(PyExc_RuntimeError, "set_splayed: failed to save table");
    return NULL;
  }
  return raypy_wrap_ray_object(ray_obj);
}

/* (get-splayed dir [sym_path]) — forward to ray_get_splayed_fn. */
PyObject *raypy_get_splayed(PyObject *self, PyObject *args) {
  (void)self;
  CHECK_MAIN_THREAD();

  RayObject *dir_obj;
  PyObject *sym_arg;

  if (!PyArg_ParseTuple(args, "O!O", &RayObjectType, &dir_obj, &sym_arg))
    return NULL;

  obj_p ray_obj;
  if (sym_arg == Py_None) {
    obj_p call_args[1] = {dir_obj->obj};
    ray_obj = ray_get_splayed_fn(call_args, 1);
  } else {
    if (!PyObject_TypeCheck(sym_arg, &RayObjectType)) {
      PyErr_SetString(PyExc_TypeError,
                      "get_splayed: sym_path must be None or RayObject");
      return NULL;
    }
    obj_p call_args[2] = {dir_obj->obj, ((RayObject *)sym_arg)->obj};
    ray_obj = ray_get_splayed_fn(call_args, 2);
  }

  if (ray_obj == NULL) {
    PyErr_SetString(PyExc_RuntimeError, "get_splayed: failed to load table");
    return NULL;
  }
  return raypy_wrap_ray_object(ray_obj);
}

/* (get-parted root name) — forward to ray_get_parted_fn. `name` must be a
 * SYM RayObject (quoted symbol atom). */
PyObject *raypy_get_parted(PyObject *self, PyObject *args) {
  (void)self;
  CHECK_MAIN_THREAD();

  RayObject *root_obj;
  RayObject *name_obj;

  if (!PyArg_ParseTuple(args, "O!O!", &RayObjectType, &root_obj, &RayObjectType,
                        &name_obj))
    return NULL;

  obj_p call_args[2] = {root_obj->obj, name_obj->obj};
  obj_p ray_obj = ray_get_parted_fn(call_args, 2);
  if (ray_obj == NULL) {
    PyErr_SetString(PyExc_RuntimeError, "get_parted: failed to load table");
    return NULL;
  }
  return raypy_wrap_ray_object(ray_obj);
}
