#include "rayforce_c.h"
#include <string.h>

static RayObject *parse_ray_object(PyObject *args) {
  RayObject *ray_obj;
  if (!PyArg_ParseTuple(args, "O!", &RayObjectType, &ray_obj))
    return NULL;
  return ray_obj;
}
static int check_type(RayObject *ray_obj, int expected_type,
                      const char *type_name) {
  if (ray_obj->obj == NULL || ray_obj->obj->type != expected_type) {
    PyErr_SetString(PyExc_RuntimeError, type_name);
    return 0;
  }
  return 1;
}

PyObject *raypy_read_i16(PyObject *self, PyObject *args) {
  (void)self;
  CHECK_MAIN_THREAD();

  RayObject *ray_obj = parse_ray_object(args);
  if (ray_obj == NULL)
    return NULL;

  if (!check_type(ray_obj, -TYPE_I16, "read: object is not an i16"))
    return NULL;

  return PyLong_FromLong(ray_obj->obj->i16);
}
PyObject *raypy_read_i32(PyObject *self, PyObject *args) {
  (void)self;
  CHECK_MAIN_THREAD();

  RayObject *ray_obj = parse_ray_object(args);
  if (ray_obj == NULL)
    return NULL;

  if (!check_type(ray_obj, -TYPE_I32, "read: object is not an i32"))
    return NULL;

  return PyLong_FromLong(ray_obj->obj->i32);
}
PyObject *raypy_read_i64(PyObject *self, PyObject *args) {
  (void)self;
  CHECK_MAIN_THREAD();

  RayObject *ray_obj = parse_ray_object(args);
  if (ray_obj == NULL)
    return NULL;

  if (!check_type(ray_obj, -TYPE_I64, "read: object is not an i64"))
    return NULL;

  return PyLong_FromLongLong(ray_obj->obj->i64);
}
PyObject *raypy_read_f64(PyObject *self, PyObject *args) {
  (void)self;
  CHECK_MAIN_THREAD();

  RayObject *ray_obj = parse_ray_object(args);
  if (ray_obj == NULL)
    return NULL;

  if (!check_type(ray_obj, -TYPE_F64, "read: object is not an f64"))
    return NULL;

  return PyFloat_FromDouble(ray_obj->obj->f64);
}
PyObject *raypy_read_c8(PyObject *self, PyObject *args) {
  (void)self;
  CHECK_MAIN_THREAD();

  RayObject *ray_obj = parse_ray_object(args);
  if (ray_obj == NULL)
    return NULL;

  /* In v2, a single character is a length-1 RAY_STR atom (SSO). */
  if (ray_obj->obj == NULL || ray_obj->obj->type != -RAY_STR) {
    PyErr_SetString(PyExc_RuntimeError, "read: object is not a c8");
    return NULL;
  }
  if (ray_str_len(ray_obj->obj) != 1) {
    PyErr_SetString(PyExc_RuntimeError, "read: c8 expects length-1 string");
    return NULL;
  }
  const char *p = ray_str_ptr(ray_obj->obj);
  return PyUnicode_FromStringAndSize(p, 1);
}
PyObject *raypy_read_string(PyObject *self, PyObject *args) {
  (void)self;
  CHECK_MAIN_THREAD();

  RayObject *ray_obj = parse_ray_object(args);
  if (ray_obj == NULL)
    return NULL;

  /* v2: strings are RAY_STR atoms (SSO or pooled). The previous TYPE_C8
   * vector form is gone — atom-only path. */
  if (ray_obj->obj == NULL || ray_obj->obj->type != -RAY_STR) {
    PyErr_SetString(PyExc_RuntimeError, "read: object is not a string");
    return NULL;
  }
  const char *p = ray_str_ptr(ray_obj->obj);
  size_t n = ray_str_len(ray_obj->obj);
  return PyUnicode_FromStringAndSize(p, (Py_ssize_t)n);
}
PyObject *raypy_read_symbol(PyObject *self, PyObject *args) {
  (void)self;
  CHECK_MAIN_THREAD();

  RayObject *ray_obj = parse_ray_object(args);
  if (ray_obj == NULL)
    return NULL;

  if (!check_type(ray_obj, -TYPE_SYMBOL, "read: object is not a symbol"))
    return NULL;

  ray_t *sstr = ray_sym_str(ray_obj->obj->i64);
  if (sstr == NULL)
    Py_RETURN_NONE;

  PyObject *result =
      PyUnicode_FromStringAndSize(ray_str_ptr(sstr), ray_str_len(sstr));
  return result;
}
PyObject *raypy_read_b8(PyObject *self, PyObject *args) {
  (void)self;
  CHECK_MAIN_THREAD();

  RayObject *ray_obj = parse_ray_object(args);
  if (ray_obj == NULL)
    return NULL;

  if (!check_type(ray_obj, -TYPE_B8, "read: object is not a b8"))
    return NULL;

  return PyBool_FromLong(ray_obj->obj->b8);
}
PyObject *raypy_read_u8(PyObject *self, PyObject *args) {
  (void)self;
  CHECK_MAIN_THREAD();

  RayObject *ray_obj = parse_ray_object(args);
  if (ray_obj == NULL)
    return NULL;

  if (!check_type(ray_obj, -TYPE_U8, "read: object is not a u8"))
    return NULL;

  return PyLong_FromLong((long)ray_obj->obj->u8);
}
PyObject *raypy_read_date(PyObject *self, PyObject *args) {
  (void)self;
  CHECK_MAIN_THREAD();

  RayObject *ray_obj = parse_ray_object(args);
  if (ray_obj == NULL)
    return NULL;

  if (!check_type(ray_obj, -TYPE_DATE, "read: object is not a date"))
    return NULL;

  return PyLong_FromLongLong(ray_obj->obj->i64);
}
PyObject *raypy_read_time(PyObject *self, PyObject *args) {
  (void)self;
  CHECK_MAIN_THREAD();

  RayObject *ray_obj = parse_ray_object(args);
  if (ray_obj == NULL)
    return NULL;

  if (!check_type(ray_obj, -TYPE_TIME, "read: object is not a time"))
    return NULL;

  return PyLong_FromLongLong(ray_obj->obj->i64);
}
PyObject *raypy_read_timestamp(PyObject *self, PyObject *args) {
  (void)self;
  CHECK_MAIN_THREAD();

  RayObject *ray_obj = parse_ray_object(args);
  if (ray_obj == NULL)
    return NULL;

  if (!check_type(ray_obj, -TYPE_TIMESTAMP, "read: object is not a timestamp"))
    return NULL;

  return PyLong_FromLongLong(ray_obj->obj->i64);
}
PyObject *raypy_read_guid(PyObject *self, PyObject *args) {
  (void)self;
  CHECK_MAIN_THREAD();

  RayObject *ray_obj = parse_ray_object(args);
  if (ray_obj == NULL)
    return NULL;

  if (!check_type(ray_obj, -TYPE_GUID, "read: object is not a guid"))
    return NULL;

  /* v2 stores GUID's 16 bytes in a U8 vector pointed to by obj->obj. */
  ray_t *bytes_vec = ray_obj->obj->obj;
  if (bytes_vec == NULL) {
    PyErr_SetString(PyExc_RuntimeError, "read: guid has no payload");
    return NULL;
  }
  return PyBytes_FromStringAndSize((const char *)ray_data(bytes_vec), 16);
}
PyObject *raypy_table_keys(PyObject *self, PyObject *args) {
  (void)self;
  CHECK_MAIN_THREAD();

  RayObject *item;
  if (!PyArg_ParseTuple(args, "O!", &RayObjectType, &item))
    return NULL;

  obj_p tbl = item->obj;
  if (tbl == NULL || tbl->type != RAY_TABLE) {
    PyErr_SetString(PyExc_RuntimeError, "read: object is not a table");
    return NULL;
  }

  int64_t ncols = ray_table_ncols(tbl);
  obj_p keys = ray_sym_vec_new(RAY_SYM_W64, ncols);
  if (keys == NULL || RAY_IS_ERR(keys)) {
    PyErr_SetString(PyExc_RuntimeError, "read: failed to allocate sym vec");
    return NULL;
  }
  int64_t *ids = (int64_t *)ray_data(keys);
  keys->len = ncols;
  for (int64_t i = 0; i < ncols; ++i) {
    ids[i] = ray_table_col_name(tbl, i);
  }
  return raypy_wrap_ray_object(keys);
}
PyObject *raypy_table_values(PyObject *self, PyObject *args) {
  (void)self;
  CHECK_MAIN_THREAD();

  RayObject *item;
  if (!PyArg_ParseTuple(args, "O!", &RayObjectType, &item))
    return NULL;

  obj_p tbl = item->obj;
  if (tbl == NULL || tbl->type != RAY_TABLE) {
    PyErr_SetString(PyExc_RuntimeError, "read: object is not a table");
    return NULL;
  }

  int64_t ncols = ray_table_ncols(tbl);
  obj_p vals = ray_list_new(ncols);
  if (vals == NULL || RAY_IS_ERR(vals)) {
    PyErr_SetString(PyExc_RuntimeError,
                    "read: failed to allocate list for values");
    return NULL;
  }
  for (int64_t i = 0; i < ncols; ++i) {
    obj_p col = ray_table_get_col_idx(tbl, i);
    if (col == NULL) {
      ray_release(vals);
      PyErr_SetString(PyExc_RuntimeError, "read: table column missing");
      return NULL;
    }
    vals = ray_list_append(vals, col);
    if (vals == NULL) {
      PyErr_SetString(PyExc_RuntimeError, "read: failed to append column");
      return NULL;
    }
  }
  return raypy_wrap_ray_object(vals);
}
PyObject *raypy_dict_keys(PyObject *self, PyObject *args) {
  (void)self;
  CHECK_MAIN_THREAD();

  RayObject *item;
  if (!PyArg_ParseTuple(args, "O!", &RayObjectType, &item))
    return NULL;

  obj_p keys = ray_key(item->obj);
  if (keys == NULL || RAY_IS_ERR(keys)) {
    PyErr_SetString(PyExc_RuntimeError, "read: dict has no keys");
    if (keys)
      ray_release(keys);
    return NULL;
  }
  return raypy_wrap_ray_object(keys);
}
PyObject *raypy_dict_values(PyObject *self, PyObject *args) {
  (void)self;
  CHECK_MAIN_THREAD();

  RayObject *item;
  if (!PyArg_ParseTuple(args, "O!", &RayObjectType, &item))
    return NULL;

  obj_p values = ray_value(item->obj);
  if (values == NULL || RAY_IS_ERR(values)) {
    PyErr_SetString(PyExc_RuntimeError, "read: dict has no values");
    if (values)
      ray_release(values);
    return NULL;
  }
  return raypy_wrap_ray_object(values);
}
PyObject *raypy_dict_get(PyObject *self, PyObject *args) {
  (void)self;
  CHECK_MAIN_THREAD();

  RayObject *item;
  RayObject *key_obj;
  if (!PyArg_ParseTuple(args, "O!O!", &RayObjectType, &item, &RayObjectType,
                        &key_obj))
    return NULL;

  obj_p result = ray_at(item->obj, key_obj->obj);
  if (result == NULL) {
    PyErr_SetString(PyExc_RuntimeError, "read: key not found in dictionary");
    return NULL;
  }
  if (RAY_IS_ERR(result)) {
    PyErr_Format(PyExc_KeyError, "read: dict lookup failed: %s",
                 ray_err_code(result));
    ray_release(result);
    return NULL;
  }
  return raypy_wrap_ray_object(result);
}
PyObject *raypy_at_idx(PyObject *self, PyObject *args) {
  (void)self;
  CHECK_MAIN_THREAD();

  RayObject *item;
  Py_ssize_t index;
  if (!PyArg_ParseTuple(args, "O!n", &RayObjectType, &item, &index))
    return NULL;

  obj_p coll = item->obj;
  if (coll == NULL) {
    PyErr_SetString(PyExc_RuntimeError, "read: collection is null");
    return NULL;
  }

  int allocated = 0;
  obj_p elem = collection_elem(coll, (int64_t)index, &allocated);
  if (elem == NULL || RAY_IS_ERR(elem)) {
    PyErr_SetString(PyExc_RuntimeError, "read: value not found at index");
    if (elem && allocated)
      ray_release(elem);
    return NULL;
  }

  if (!allocated) {
    /* Borrowed pointer — bump rc so Python wrapper owns its share. */
    ray_retain(elem);
  }
  return raypy_wrap_ray_object(elem);
}
PyObject *raypy_get_obj_length(PyObject *self, PyObject *args) {
  (void)self;
  CHECK_MAIN_THREAD();

  RayObject *ray_obj;
  if (!PyArg_ParseTuple(args, "O!", &RayObjectType, &ray_obj))
    return NULL;

  obj_p o = ray_obj->obj;
  if (o == NULL) {
    PyErr_SetString(PyExc_RuntimeError, "read: object is null");
    return NULL;
  }
  if (o->type == RAY_TABLE) {
    return PyLong_FromLongLong(ray_table_nrows(o));
  }
  if (o->type == -RAY_STR) {
    return PyLong_FromUnsignedLongLong(ray_str_len(o));
  }
  return PyLong_FromLongLong(o->len);
}
PyObject *raypy_repr_table(PyObject *self, PyObject *args) {
  (void)self;
  CHECK_MAIN_THREAD();

  RayObject *ray_obj;
  int full = 1;
  if (!PyArg_ParseTuple(args, "O!|p", &RayObjectType, &ray_obj, &full))
    return NULL;

  obj_p s = ray_fmt(ray_obj->obj, full ? 1 : 0);
  if (s == NULL || RAY_IS_ERR(s)) {
    PyErr_SetString(PyExc_RuntimeError, "read: failed to format object");
    if (s)
      ray_release(s);
    return NULL;
  }

  PyObject *result =
      PyUnicode_FromStringAndSize(ray_str_ptr(s), (Py_ssize_t)ray_str_len(s));
  ray_release(s);
  return result;
}
/* Build a 2-entry ray dict `{code: <code>, message: <msg>}` from the error. */
static obj_p build_err_dict(const char *code, const char *msg) {
  /* Keys vec: SYM vec of width 64 with two ids. */
  obj_p keys = ray_sym_vec_new(RAY_SYM_W64, 2);
  if (keys == NULL || RAY_IS_ERR(keys))
    return keys;
  int64_t *ids = (int64_t *)ray_data(keys);
  ids[0] = ray_sym_intern("code", 4);
  ids[1] = ray_sym_intern("message", 7);
  if (ids[0] < 0 || ids[1] < 0) {
    ray_release(keys);
    return NULL;
  }
  keys->len = 2;

  obj_p code_atom = ray_str(code ? code : "err", strlen(code ? code : "err"));
  obj_p msg_atom = ray_str(msg ? msg : "", msg ? strlen(msg) : 0);
  if (code_atom == NULL || RAY_IS_ERR(code_atom) || msg_atom == NULL ||
      RAY_IS_ERR(msg_atom)) {
    ray_release(keys);
    if (code_atom)
      ray_release(code_atom);
    if (msg_atom)
      ray_release(msg_atom);
    return NULL;
  }

  obj_p vals = ray_list_new(2);
  if (vals == NULL || RAY_IS_ERR(vals)) {
    ray_release(keys);
    ray_release(code_atom);
    ray_release(msg_atom);
    return vals;
  }
  vals = ray_list_append(vals, code_atom);
  ray_release(code_atom);
  if (vals == NULL || RAY_IS_ERR(vals)) {
    ray_release(keys);
    ray_release(msg_atom);
    return vals;
  }
  vals = ray_list_append(vals, msg_atom);
  ray_release(msg_atom);
  if (vals == NULL || RAY_IS_ERR(vals)) {
    ray_release(keys);
    return vals;
  }

  obj_p dict = ray_dict_fn(keys, vals);
  ray_release(keys);
  ray_release(vals);
  return dict;
}

PyObject *raypy_get_error_obj(PyObject *self, PyObject *args) {
  (void)self;
  CHECK_MAIN_THREAD();

  RayObject *item;
  if (!PyArg_ParseTuple(args, "O!", &RayObjectType, &item))
    return NULL;

  obj_p err = item->obj;
  const char *code = "unknown";
  const char *msg = "";
  if (err != NULL && RAY_IS_ERR(err)) {
    code = ray_err_code(err);
    msg = ray_error_msg();
    if (!code)
      code = "err";
    if (!msg)
      msg = "";
  }

  obj_p dict = build_err_dict(code, msg);
  if (dict == NULL || RAY_IS_ERR(dict)) {
    if (dict)
      ray_release(dict);
    PyErr_SetString(PyExc_RuntimeError, "read: failed to build error dict");
    return NULL;
  }
  return raypy_wrap_ray_object(dict);
}
PyObject *raypy_env_get_internal_fn_by_name(PyObject *self, PyObject *args) {
  (void)self;
  CHECK_MAIN_THREAD();

  const char *name;
  Py_ssize_t name_len;
  if (!PyArg_ParseTuple(args, "s#", &name, &name_len))
    return NULL;

  int64_t sym_id = ray_sym_intern(name, (size_t)name_len);
  if (sym_id < 0) {
    PyErr_SetString(PyExc_RuntimeError, "read: failed to intern function name");
    return NULL;
  }

  obj_p func_obj = ray_env_get(sym_id);
  if (func_obj == NULL_OBJ || func_obj == NULL) {
    PyErr_SetString(PyExc_RuntimeError, "read: function not found");
    return NULL;
  }

  ray_retain(func_obj);
  return raypy_wrap_ray_object(func_obj);
}
PyObject *raypy_env_get_internal_name_by_fn(PyObject *self, PyObject *args) {
  (void)self;
  CHECK_MAIN_THREAD();

  RayObject *ray_obj;
  if (!PyArg_ParseTuple(args, "O!", &RayObjectType, &ray_obj))
    return NULL;

  PyErr_SetString(
      PyExc_NotImplementedError,
      "env_get_internal_name_by_fn is not supported on rayforce v2");
  return NULL;
}
PyObject *raypy_get_obj_type(PyObject *self, PyObject *args) {
  (void)self;
  CHECK_MAIN_THREAD();

  RayObject *ray_obj;
  if (!PyArg_ParseTuple(args, "O!", &RayObjectType, &ray_obj))
    return NULL;

  if (ray_obj->obj == NULL) {
    PyErr_SetString(PyExc_RuntimeError, "read: object is null");
    return NULL;
  }
  /* v2: dict is RAY_LIST + RAY_ATTR_DICT. Synthesize RAY_DICT for Python. */
  if (ray_obj->obj->type == RAY_LIST && (ray_obj->obj->attrs & RAY_ATTR_DICT)) {
    return PyLong_FromLong(RAY_DICT);
  }
  return PyLong_FromLong(ray_obj->obj->type);
}
PyObject *raypy_rc(PyObject *self, PyObject *args) {
  (void)self;
  CHECK_MAIN_THREAD();

  RayObject *ray_obj;
  if (!PyArg_ParseTuple(args, "O!", &RayObjectType, &ray_obj))
    return NULL;

  return PyLong_FromUnsignedLong(rc_obj(ray_obj->obj));
}
PyObject *raypy_vec_is_null(PyObject *self, PyObject *args) {
  (void)self;
  CHECK_MAIN_THREAD();

  RayObject *ray_obj;
  Py_ssize_t idx;
  if (!PyArg_ParseTuple(args, "O!n", &RayObjectType, &ray_obj, &idx))
    return NULL;

  obj_p vec = ray_obj->obj;
  if (vec == NULL) {
    PyErr_SetString(PyExc_RuntimeError, "vec_is_null: object is null");
    return NULL;
  }
  if (!ray_is_vec(vec)) {
    PyErr_SetString(PyExc_RuntimeError, "vec_is_null: object is not a vector");
    return NULL;
  }
  if (idx < 0 || idx >= vec->len) {
    PyErr_Format(PyExc_IndexError,
                 "vec_is_null: index %zd out of range (len %lld)", idx,
                 (long long)vec->len);
    return NULL;
  }
  return PyBool_FromLong(ray_vec_is_null(vec, (int64_t)idx));
}
PyObject *raypy_vec_set_null(PyObject *self, PyObject *args) {
  (void)self;
  CHECK_MAIN_THREAD();

  RayObject *ray_obj;
  Py_ssize_t idx;
  int is_null;
  if (!PyArg_ParseTuple(args, "O!np", &RayObjectType, &ray_obj, &idx, &is_null))
    return NULL;

  obj_p vec = ray_obj->obj;
  if (vec == NULL) {
    PyErr_SetString(PyExc_RuntimeError, "vec_set_null: object is null");
    return NULL;
  }
  if (!ray_is_vec(vec)) {
    PyErr_SetString(PyExc_RuntimeError, "vec_set_null: object is not a vector");
    return NULL;
  }
  if (idx < 0 || idx >= vec->len) {
    PyErr_Format(PyExc_IndexError,
                 "vec_set_null: index %zd out of range (len %lld)", idx,
                 (long long)vec->len);
    return NULL;
  }
  ray_vec_set_null(vec, (int64_t)idx, is_null ? true : false);
  Py_RETURN_NONE;
}
