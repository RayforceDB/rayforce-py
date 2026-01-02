#include "rayforce_c.h"

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

  if (!check_type(ray_obj, -TYPE_C8, "read: object is not a c8"))
    return NULL;

  return PyUnicode_FromStringAndSize(&ray_obj->obj->c8, 1);
}
PyObject *raypy_read_string(PyObject *self, PyObject *args) {
  (void)self;
  CHECK_MAIN_THREAD();

  RayObject *ray_obj = parse_ray_object(args);
  if (ray_obj == NULL)
    return NULL;

  if (!check_type(ray_obj, TYPE_C8, "read: object is not a string"))
    return NULL;

  return PyUnicode_FromStringAndSize(AS_C8(ray_obj->obj), ray_obj->obj->len);
}
PyObject *raypy_read_symbol(PyObject *self, PyObject *args) {
  (void)self;
  CHECK_MAIN_THREAD();

  RayObject *ray_obj = parse_ray_object(args);
  if (ray_obj == NULL)
    return NULL;

  if (!check_type(ray_obj, -TYPE_SYMBOL, "read: object is not a symbol"))
    return NULL;

  const char *str = str_from_symbol(ray_obj->obj->i64);
  if (str == NULL)
    Py_RETURN_NONE;

  return PyUnicode_FromString(str);
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

  return PyLong_FromLong(ray_obj->obj->i32);
}
PyObject *raypy_read_time(PyObject *self, PyObject *args) {
  (void)self;
  CHECK_MAIN_THREAD();

  RayObject *ray_obj = parse_ray_object(args);
  if (ray_obj == NULL)
    return NULL;

  if (!check_type(ray_obj, -TYPE_TIME, "read: object is not a time"))
    return NULL;

  return PyLong_FromLong(ray_obj->obj->i32);
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

  return PyBytes_FromStringAndSize((const char *)AS_U8(ray_obj->obj), 16);
}
PyObject *raypy_table_keys(PyObject *self, PyObject *args) {
  (void)self;
  CHECK_MAIN_THREAD();

  RayObject *item;
  if (!PyArg_ParseTuple(args, "O!", &RayObjectType, &item))
    return NULL;

  obj_p keys = AS_LIST(item->obj)[0];
  if (keys == NULL) {
    PyErr_SetString(PyExc_RuntimeError, "read: table has no keys");
    return NULL;
  }

  obj_p ray_obj = clone_obj(keys);
  if (ray_obj == NULL) {
    PyErr_SetString(PyExc_RuntimeError, "read: failed to clone table keys");
    return NULL;
  }
  return raypy_wrap_ray_object(ray_obj);
}
PyObject *raypy_table_values(PyObject *self, PyObject *args) {
  (void)self;
  CHECK_MAIN_THREAD();

  RayObject *item;
  if (!PyArg_ParseTuple(args, "O!", &RayObjectType, &item))
    return NULL;

  obj_p values = AS_LIST(item->obj)[1];
  if (values == NULL) {
    PyErr_SetString(PyExc_RuntimeError, "read: table has no values");
    return NULL;
  }

  obj_p ray_obj = clone_obj(values);
  if (ray_obj == NULL) {
    PyErr_SetString(PyExc_RuntimeError, "read: failed to clone table values");
    return NULL;
  }
  return raypy_wrap_ray_object(ray_obj);
}
PyObject *raypy_dict_keys(PyObject *self, PyObject *args) {
  (void)self;
  CHECK_MAIN_THREAD();

  RayObject *item;
  if (!PyArg_ParseTuple(args, "O!", &RayObjectType, &item))
    return NULL;

  obj_p keys = ray_key(item->obj);
  if (keys == NULL) {
    PyErr_SetString(PyExc_RuntimeError, "read: dict has no keys");
    return NULL;
  }

  obj_p ray_obj = clone_obj(keys);
  if (ray_obj == NULL) {
    PyErr_SetString(PyExc_RuntimeError, "read: failed to clone dict keys");
    return NULL;
  }
  return raypy_wrap_ray_object(ray_obj);
}
PyObject *raypy_dict_values(PyObject *self, PyObject *args) {
  (void)self;
  CHECK_MAIN_THREAD();

  RayObject *item;
  if (!PyArg_ParseTuple(args, "O!", &RayObjectType, &item))
    return NULL;

  obj_p values = ray_value(item->obj);
  if (values == NULL) {
    PyErr_SetString(PyExc_RuntimeError, "read: dict has no values");
    return NULL;
  }

  obj_p ray_obj = clone_obj(values);
  if (ray_obj == NULL) {
    PyErr_SetString(PyExc_RuntimeError, "read: failed to clone dict values");
    return NULL;
  }
  return raypy_wrap_ray_object(ray_obj);
}
PyObject *raypy_dict_get(PyObject *self, PyObject *args) {
  (void)self;
  CHECK_MAIN_THREAD();

  RayObject *item;
  RayObject *key_obj;
  if (!PyArg_ParseTuple(args, "O!O!", &RayObjectType, &item, &RayObjectType,
                        &key_obj))
    return NULL;

  obj_p result = at_obj(item->obj, key_obj->obj);
  if (result == NULL) {
    PyErr_SetString(PyExc_RuntimeError, "read: key not found in dictionary");
    return NULL;
  }

  obj_p ray_obj = clone_obj(result);
  if (ray_obj == NULL) {
    PyErr_SetString(PyExc_RuntimeError,
                    "read: failed to clone dictionary value");
    return NULL;
  }
  return raypy_wrap_ray_object(ray_obj);
}
PyObject *raypy_at_idx(PyObject *self, PyObject *args) {
  (void)self;
  CHECK_MAIN_THREAD();

  RayObject *item;
  Py_ssize_t index;
  if (!PyArg_ParseTuple(args, "O!n", &RayObjectType, &item, &index))
    return NULL;

  obj_p result = at_idx(item->obj, (i64_t)index);
  if (result == NULL) {
    PyErr_SetString(PyExc_RuntimeError, "read: value not found at index");
    return NULL;
  }

  obj_p ray_obj = clone_obj(result);
  if (ray_obj == NULL) {
    PyErr_SetString(PyExc_RuntimeError, "read: failed to clone item at index");
    return NULL;
  }
  return raypy_wrap_ray_object(ray_obj);
}
PyObject *raypy_get_obj_length(PyObject *self, PyObject *args) {
  (void)self;
  CHECK_MAIN_THREAD();

  RayObject *ray_obj;
  if (!PyArg_ParseTuple(args, "O!", &RayObjectType, &ray_obj))
    return NULL;

  return PyLong_FromUnsignedLongLong(ray_obj->obj->len);
}
PyObject *raypy_repr_table(PyObject *self, PyObject *args) {
  (void)self;
  CHECK_MAIN_THREAD();

  RayObject *ray_obj;
  int full = 1;
  if (!PyArg_ParseTuple(args, "O!|p", &RayObjectType, &ray_obj, &full))
    return NULL;

  obj_p item = obj_fmt(ray_obj->obj, (b8_t)full);
  if (item == NULL) {
    PyErr_SetString(PyExc_RuntimeError, "read: failed to format table");
    return NULL;
  }

  PyObject *result = PyUnicode_FromStringAndSize(AS_C8(item), item->len);
  drop_obj(item);
  return result;
}
PyObject *raypy_get_error_obj(PyObject *self, PyObject *args) {
  (void)self;
  CHECK_MAIN_THREAD();

  RayObject *item;
  if (!PyArg_ParseTuple(args, "O!", &RayObjectType, &item))
    return NULL;

  obj_p err = item->obj;
  if (err == NULL || err->type != TYPE_ERR) {
    return PyUnicode_FromString("Unknown error");
  }

  obj_p ray_obj = err_info(err);
  if (ray_obj == NULL) {
    PyErr_SetString(PyExc_RuntimeError, "read: failed to get error info");
    return NULL;
  }
  return raypy_wrap_ray_object(ray_obj);
}
PyObject *raypy_env_get_internal_fn_by_name(PyObject *self, PyObject *args) {
  (void)self;
  CHECK_MAIN_THREAD();

  const char *name;
  Py_ssize_t name_len;
  if (!PyArg_ParseTuple(args, "s#", &name, &name_len))
    return NULL;

  obj_p func_obj = env_get_internal_function(name);
  if (func_obj == NULL_OBJ || func_obj == NULL) {
    PyErr_SetString(PyExc_RuntimeError, "read: function not found");
    return NULL;
  }

  obj_p ray_obj = clone_obj(func_obj);
  if (ray_obj == NULL) {
    PyErr_SetString(PyExc_RuntimeError,
                    "read: failed to clone internal function");
    return NULL;
  }
  return raypy_wrap_ray_object(ray_obj);
}
PyObject *raypy_env_get_internal_name_by_fn(PyObject *self, PyObject *args) {
  (void)self;
  CHECK_MAIN_THREAD();

  RayObject *ray_obj;
  if (!PyArg_ParseTuple(args, "O!", &RayObjectType, &ray_obj))
    return NULL;

  str_p name = env_get_internal_name(ray_obj->obj);
  if (name == NULL) {
    PyErr_SetString(PyExc_RuntimeError, "read: function name not found");
    return NULL;
  }
  return PyUnicode_FromString(name);
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
