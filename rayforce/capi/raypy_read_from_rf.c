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
    PyErr_SetString(PyExc_TypeError, type_name);
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

  if (!check_type(ray_obj, -TYPE_I16, "Object is not an i16"))
    return NULL;

  return PyLong_FromLong(ray_obj->obj->i16);
}
PyObject *raypy_read_i32(PyObject *self, PyObject *args) {
  (void)self;
  CHECK_MAIN_THREAD();

  RayObject *ray_obj = parse_ray_object(args);
  if (ray_obj == NULL)
    return NULL;

  if (!check_type(ray_obj, -TYPE_I32, "Object is not an i32"))
    return NULL;

  return PyLong_FromLong(ray_obj->obj->i32);
}
PyObject *raypy_read_i64(PyObject *self, PyObject *args) {
  (void)self;
  CHECK_MAIN_THREAD();

  RayObject *ray_obj = parse_ray_object(args);
  if (ray_obj == NULL)
    return NULL;

  if (!check_type(ray_obj, -TYPE_I64, "Object is not an i64"))
    return NULL;

  return PyLong_FromLongLong(ray_obj->obj->i64);
}
PyObject *raypy_read_f64(PyObject *self, PyObject *args) {
  (void)self;
  CHECK_MAIN_THREAD();

  RayObject *ray_obj = parse_ray_object(args);
  if (ray_obj == NULL)
    return NULL;

  if (!check_type(ray_obj, -TYPE_F64, "Object is not an f64"))
    return NULL;

  return PyFloat_FromDouble(ray_obj->obj->f64);
}
PyObject *raypy_read_c8(PyObject *self, PyObject *args) {
  (void)self;
  CHECK_MAIN_THREAD();

  RayObject *ray_obj = parse_ray_object(args);
  if (ray_obj == NULL)
    return NULL;

  if (!check_type(ray_obj, -TYPE_C8, "Object is not a c8"))
    return NULL;

  return PyUnicode_FromStringAndSize(&ray_obj->obj->c8, 1);
}
PyObject *raypy_read_string(PyObject *self, PyObject *args) {
  (void)self;
  CHECK_MAIN_THREAD();

  RayObject *ray_obj = parse_ray_object(args);
  if (ray_obj == NULL)
    return NULL;

  if (!check_type(ray_obj, TYPE_C8, "Object is not a string"))
    return NULL;

  return PyUnicode_FromStringAndSize(AS_C8(ray_obj->obj), ray_obj->obj->len);
}
PyObject *raypy_read_symbol(PyObject *self, PyObject *args) {
  (void)self;
  CHECK_MAIN_THREAD();

  RayObject *ray_obj = parse_ray_object(args);
  if (ray_obj == NULL)
    return NULL;

  if (!check_type(ray_obj, -TYPE_SYMBOL, "Object is not a symbol"))
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

  if (!check_type(ray_obj, -TYPE_B8, "Object is not a B8 type"))
    return NULL;

  return PyBool_FromLong(ray_obj->obj->b8);
}
PyObject *raypy_read_u8(PyObject *self, PyObject *args) {
  (void)self;
  CHECK_MAIN_THREAD();

  RayObject *ray_obj = parse_ray_object(args);
  if (ray_obj == NULL)
    return NULL;

  if (!check_type(ray_obj, -TYPE_U8, "Object is not a U8 type"))
    return NULL;

  return PyLong_FromLong((long)ray_obj->obj->u8);
}
PyObject *raypy_read_date(PyObject *self, PyObject *args) {
  (void)self;
  CHECK_MAIN_THREAD();

  RayObject *ray_obj = parse_ray_object(args);
  if (ray_obj == NULL)
    return NULL;

  if (!check_type(ray_obj, -TYPE_DATE, "Object is not a DATE type"))
    return NULL;

  return PyLong_FromLong(ray_obj->obj->i32);
}
PyObject *raypy_read_time(PyObject *self, PyObject *args) {
  (void)self;
  CHECK_MAIN_THREAD();

  RayObject *ray_obj = parse_ray_object(args);
  if (ray_obj == NULL)
    return NULL;

  if (!check_type(ray_obj, -TYPE_TIME, "Object is not a TIME type"))
    return NULL;

  return PyLong_FromLong(ray_obj->obj->i32);
}
PyObject *raypy_read_timestamp(PyObject *self, PyObject *args) {
  (void)self;
  CHECK_MAIN_THREAD();

  RayObject *ray_obj = parse_ray_object(args);
  if (ray_obj == NULL)
    return NULL;

  if (!check_type(ray_obj, -TYPE_TIMESTAMP, "Object is not a TIMESTAMP type"))
    return NULL;

  return PyLong_FromLongLong(ray_obj->obj->i64);
}
PyObject *raypy_read_guid(PyObject *self, PyObject *args) {
  (void)self;
  CHECK_MAIN_THREAD();

  RayObject *ray_obj = parse_ray_object(args);
  if (ray_obj == NULL)
    return NULL;

  if (!check_type(ray_obj, -TYPE_GUID, "Object is not a GUID type"))
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
    PyErr_SetString(PyExc_RuntimeError, "Table has no keys");
    return NULL;
  }

  obj_p ray_obj = clone_obj(keys);
  if (ray_obj == NULL) {
    PyErr_SetString(PyExc_MemoryError, "Failed to clone keys");
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
    PyErr_SetString(PyExc_RuntimeError, "Table has no values");
    return NULL;
  }

  obj_p ray_obj = clone_obj(values);
  if (ray_obj == NULL) {
    PyErr_SetString(PyExc_MemoryError, "Failed to clone values");
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
    PyErr_SetString(PyExc_RuntimeError, "Dict has no keys");
    return NULL;
  }

  obj_p ray_obj = clone_obj(keys);
  if (ray_obj == NULL) {
    PyErr_SetString(PyExc_MemoryError, "Failed to clone dict keys");
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
    PyErr_SetString(PyExc_RuntimeError, "Dict has no values");
    return NULL;
  }

  obj_p ray_obj = clone_obj(values);
  if (ray_obj == NULL) {
    PyErr_SetString(PyExc_MemoryError, "Failed to clone dict values");
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
    PyErr_SetString(PyExc_KeyError, "Key not found in dictionary");
    return NULL;
  }

  obj_p ray_obj = clone_obj(result);
  if (ray_obj == NULL) {
    PyErr_SetString(PyExc_MemoryError, "Failed to clone dictionary value");
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
  if (item == NULL) {
    PyErr_SetString(PyExc_KeyError, "Value not found at index");
    return NULL;
  }

  obj_p ray_obj = clone_obj(result);
  if (ray_obj == NULL) {
    PyErr_SetString(PyExc_MemoryError, "Failed to clone item");
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
    PyErr_SetString(PyExc_RuntimeError, "Failed to format object");
    return NULL;
  }

  PyObject *result = PyUnicode_FromStringAndSize(AS_C8(item), item->len);
  drop_obj(item);
  return result;
}
PyObject *raypy_get_error_obj(PyObject *self, PyObject *args) {
  (void)self;
  CHECK_MAIN_THREAD();
  RayObject *ray_obj;

  if (!PyArg_ParseTuple(args, "O!", &RayObjectType, &ray_obj))
    return NULL;

  obj_p err = ray_obj->obj;
  if (err == NULL || err->type != TYPE_ERR) {
    return PyUnicode_FromString("Unknown error");
  }

  obj_p result_dict = err_info(err);
  RayObject *result = (RayObject *)RayObjectType.tp_alloc(&RayObjectType, 0);
  if (result == NULL) {
    drop_obj(result_dict);
    return NULL;
  }

  result->obj = clone_obj(result_dict);
  drop_obj(result_dict);
  if (result->obj == NULL || result->obj == NULL_OBJ) {
    Py_DECREF(result);
    PyErr_SetString(PyExc_MemoryError, "Failed to clone error info dict");
    return NULL;
  }

  return (PyObject *)result;
}
PyObject *raypy_env_get_internal_function_by_name(PyObject *self,
                                                  PyObject *args) {
  (void)self;
  CHECK_MAIN_THREAD();
  const char *name;
  Py_ssize_t name_len;

  if (!PyArg_ParseTuple(args, "s#", &name, &name_len))
    return NULL;

  obj_p func_obj = env_get_internal_function(name);

  if (func_obj == NULL_OBJ || func_obj == NULL) {
    PyErr_SetString(PyExc_RuntimeError, "Function not found");
    return NULL;
  }

  obj_p ray_obj = clone_obj(func_obj);
  if (ray_obj == NULL) {
    PyErr_SetString(PyExc_MemoryError, "Failed to clone internal function");
    return NULL;
  }
  return raypy_wrap_ray_object(ray_obj);
}
PyObject *raypy_env_get_internal_name_by_function(PyObject *self,
                                                  PyObject *args) {
  (void)self;
  CHECK_MAIN_THREAD();
  RayObject *ray_obj;

  if (!PyArg_ParseTuple(args, "O!", &RayObjectType, &ray_obj))
    return NULL;

  str_p name = env_get_internal_name(ray_obj->obj);
  if (name == NULL) {
    PyErr_SetString(PyExc_RuntimeError, "Function not found");
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
    PyErr_SetString(PyExc_ValueError, "Object is NULL");
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
