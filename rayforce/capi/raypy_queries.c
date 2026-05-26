#include "rayforce_c.h"

/* Decode an Optional[RayObject] Python arg. Writes the underlying ray_t*
 * into *out (NULL if `arg` is Py_None) and returns 0; returns -1 with PyErr
 * set when the type is wrong. */
static int unpack_optional_ray(PyObject *arg, ray_t **out,
                               const char *fn_name, const char *arg_name) {
  if (arg == Py_None) {
    *out = NULL;
    return 0;
  }
  if (!PyObject_TypeCheck(arg, &RayObjectType)) {
    PyErr_Format(PyExc_TypeError, "%s: %s must be None or RayObject",
                 fn_name, arg_name);
    return -1;
  }
  *out = ((RayObject *)arg)->obj;
  return 0;
}

PyObject *raypy_update(PyObject *self, PyObject *args) {
  (void)self;
  CHECK_MAIN_THREAD();

  RayObject *update_dict;

  if (!PyArg_ParseTuple(args, "O!", &RayObjectType, &update_dict))
    return NULL;

  ray_t *call_args[1] = {update_dict->obj};
  ray_t *ray_obj = ray_update_fn(call_args, 1);
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

  ray_t *call_args[2] = {table_obj->obj, data_obj->obj};
  ray_t *ray_obj = ray_insert_fn(call_args, 2);
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

  ray_t *call_args[3] = {table_obj->obj, keys_obj->obj, data_obj->obj};
  ray_t *ray_obj = ray_upsert_fn(call_args, 3);
  if (ray_obj == NULL) {
    PyErr_SetString(PyExc_RuntimeError,
                    "query: failed to execute upsert query");
    return NULL;
  }
  return raypy_wrap_ray_object(ray_obj);
}

/* (.csv.read [schema] path) — schema is a RAY_SYM vector of UPPERCASE type
 * names ("I64", "F64", "B8", "DATE", "TIME", "TIMESTAMP", "SYMBOL", "STR",
 * "GUID", "I32", "I16", "U8"). */
PyObject *raypy_read_csv(PyObject *self, PyObject *args) {
  (void)self;
  CHECK_MAIN_THREAD();

  PyObject *schema_arg;
  RayObject *path_obj;

  if (!PyArg_ParseTuple(args, "OO!", &schema_arg, &RayObjectType, &path_obj))
    return NULL;

  ray_t *schema_obj = NULL;
  if (unpack_optional_ray(schema_arg, &schema_obj, "read_csv", "schema") < 0)
    return NULL;

  ray_t *call_args[2];
  int nargs;
  if (schema_obj) {
    call_args[0] = schema_obj;
    call_args[1] = path_obj->obj;
    nargs = 2;
  } else {
    call_args[0] = path_obj->obj;
    nargs = 1;
  }
  ray_t *ray_obj = ray_read_csv_fn(call_args, nargs);
  if (ray_obj == NULL) {
    PyErr_SetString(PyExc_RuntimeError, "read_csv: failed to read CSV");
    return NULL;
  }
  return raypy_wrap_ray_object(ray_obj);
}

/* (.csv.write table path) */
PyObject *raypy_write_csv(PyObject *self, PyObject *args) {
  (void)self;
  CHECK_MAIN_THREAD();

  RayObject *table_obj;
  RayObject *path_obj;

  if (!PyArg_ParseTuple(args, "O!O!", &RayObjectType, &table_obj,
                        &RayObjectType, &path_obj))
    return NULL;

  ray_t *call_args[2] = {table_obj->obj, path_obj->obj};
  ray_t *ray_obj = ray_write_csv_fn(call_args, 2);
  if (ray_obj == NULL) {
    PyErr_SetString(PyExc_RuntimeError, "write_csv: failed to write CSV");
    return NULL;
  }
  return raypy_wrap_ray_object(ray_obj);
}

/* (.db.splayed.set dir table [sym_path]) — when sym_arg is None the core
 * picks a default sym path; otherwise it must be a STR RayObject. */
PyObject *raypy_set_splayed(PyObject *self, PyObject *args) {
  (void)self;
  CHECK_MAIN_THREAD();

  RayObject *dir_obj;
  RayObject *table_obj;
  PyObject *sym_arg;

  if (!PyArg_ParseTuple(args, "O!O!O", &RayObjectType, &dir_obj, &RayObjectType,
                        &table_obj, &sym_arg))
    return NULL;

  ray_t *sym_obj = NULL;
  if (unpack_optional_ray(sym_arg, &sym_obj, "set_splayed", "sym_path") < 0)
    return NULL;

  ray_t *call_args[3] = {dir_obj->obj, table_obj->obj, sym_obj};
  ray_t *ray_obj = ray_set_splayed_fn(call_args, sym_obj ? 3 : 2);
  if (ray_obj == NULL) {
    PyErr_SetString(PyExc_RuntimeError, "set_splayed: failed to save table");
    return NULL;
  }
  return raypy_wrap_ray_object(ray_obj);
}

/* (.db.splayed.get dir [sym_path]) */
PyObject *raypy_get_splayed(PyObject *self, PyObject *args) {
  (void)self;
  CHECK_MAIN_THREAD();

  RayObject *dir_obj;
  PyObject *sym_arg;

  if (!PyArg_ParseTuple(args, "O!O", &RayObjectType, &dir_obj, &sym_arg))
    return NULL;

  ray_t *sym_obj = NULL;
  if (unpack_optional_ray(sym_arg, &sym_obj, "get_splayed", "sym_path") < 0)
    return NULL;

  ray_t *call_args[2] = {dir_obj->obj, sym_obj};
  ray_t *ray_obj = ray_get_splayed_fn(call_args, sym_obj ? 2 : 1);
  if (ray_obj == NULL) {
    PyErr_SetString(PyExc_RuntimeError, "get_splayed: failed to load table");
    return NULL;
  }
  return raypy_wrap_ray_object(ray_obj);
}

/* (.db.parted.get root name) — `name` must be a SYM RayObject (quoted
 * symbol atom). */
PyObject *raypy_get_parted(PyObject *self, PyObject *args) {
  (void)self;
  CHECK_MAIN_THREAD();

  RayObject *root_obj;
  RayObject *name_obj;

  if (!PyArg_ParseTuple(args, "O!O!", &RayObjectType, &root_obj, &RayObjectType,
                        &name_obj))
    return NULL;

  ray_t *call_args[2] = {root_obj->obj, name_obj->obj};
  ray_t *ray_obj = ray_get_parted_fn(call_args, 2);
  if (ray_obj == NULL) {
    PyErr_SetString(PyExc_RuntimeError, "get_parted: failed to load table");
    return NULL;
  }
  return raypy_wrap_ray_object(ray_obj);
}
