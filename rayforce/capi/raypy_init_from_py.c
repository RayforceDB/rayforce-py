#include "rayforce_c.h"
#include <stdio.h>

PyObject *raypy_init_i16(PyObject *self, PyObject *args) {
  (void)self;
  CHECK_MAIN_THREAD();

  PyObject *item;
  if (!PyArg_ParseTuple(args, "O", &item))
    return NULL;

  obj_p ray_obj = raypy_init_i16_from_py(item);
  if (ray_obj == NULL)
    return NULL;
  return raypy_wrap_ray_object(ray_obj);
}
PyObject *raypy_init_i32(PyObject *self, PyObject *args) {
  (void)self;
  CHECK_MAIN_THREAD();

  PyObject *item;
  if (!PyArg_ParseTuple(args, "O", &item))
    return NULL;

  obj_p ray_obj = raypy_init_i32_from_py(item);
  if (ray_obj == NULL)
    return NULL;
  return raypy_wrap_ray_object(ray_obj);
}
PyObject *raypy_init_i64(PyObject *self, PyObject *args) {
  (void)self;
  CHECK_MAIN_THREAD();

  PyObject *item;
  if (!PyArg_ParseTuple(args, "O", &item))
    return NULL;

  obj_p ray_obj = raypy_init_i64_from_py(item);
  if (ray_obj == NULL)
    return NULL;
  return raypy_wrap_ray_object(ray_obj);
}
PyObject *raypy_init_f64(PyObject *self, PyObject *args) {
  (void)self;
  CHECK_MAIN_THREAD();

  PyObject *item;
  if (!PyArg_ParseTuple(args, "O", &item))
    return NULL;

  obj_p ray_obj = raypy_init_f64_from_py(item);
  if (ray_obj == NULL)
    return NULL;
  return raypy_wrap_ray_object(ray_obj);
}
PyObject *raypy_init_c8(PyObject *self, PyObject *args) {
  (void)self;
  CHECK_MAIN_THREAD();

  PyObject *item;
  if (!PyArg_ParseTuple(args, "O", &item))
    return NULL;

  obj_p ray_obj = raypy_init_c8_from_py(item);
  if (ray_obj == NULL)
    return NULL;
  return raypy_wrap_ray_object(ray_obj);
}
PyObject *raypy_init_string(PyObject *self, PyObject *args) {
  (void)self;
  CHECK_MAIN_THREAD();

  PyObject *item;
  if (!PyArg_ParseTuple(args, "O", &item))
    return NULL;

  obj_p ray_obj = raypy_init_string_from_py(item);
  if (ray_obj == NULL)
    return NULL;
  return raypy_wrap_ray_object(ray_obj);
}
PyObject *raypy_init_symbol(PyObject *self, PyObject *args) {
  (void)self;
  CHECK_MAIN_THREAD();

  PyObject *item;
  if (!PyArg_ParseTuple(args, "O", &item))
    return NULL;

  obj_p ray_obj = raypy_init_symbol_from_py(item);
  if (ray_obj == NULL)
    return NULL;
  return raypy_wrap_ray_object(ray_obj);
}
PyObject *raypy_init_b8(PyObject *self, PyObject *args) {
  (void)self;
  CHECK_MAIN_THREAD();

  PyObject *item;
  if (!PyArg_ParseTuple(args, "O", &item))
    return NULL;

  obj_p ray_obj = raypy_init_b8_from_py(item);
  if (ray_obj == NULL)
    return NULL;
  return raypy_wrap_ray_object(ray_obj);
}
PyObject *raypy_init_u8(PyObject *self, PyObject *args) {
  (void)self;
  CHECK_MAIN_THREAD();

  PyObject *item;
  if (!PyArg_ParseTuple(args, "O", &item))
    return NULL;

  obj_p ray_obj = raypy_init_u8_from_py(item);
  if (ray_obj == NULL)
    return NULL;
  return raypy_wrap_ray_object(ray_obj);
}
PyObject *raypy_init_date(PyObject *self, PyObject *args) {
  (void)self;
  CHECK_MAIN_THREAD();

  PyObject *item;
  if (!PyArg_ParseTuple(args, "O", &item))
    return NULL;

  obj_p ray_obj = raypy_init_date_from_py(item);
  if (ray_obj == NULL)
    return NULL;
  return raypy_wrap_ray_object(ray_obj);
}
PyObject *raypy_init_time(PyObject *self, PyObject *args) {
  (void)self;
  CHECK_MAIN_THREAD();

  PyObject *item;
  if (!PyArg_ParseTuple(args, "O", &item))
    return NULL;

  obj_p ray_obj = raypy_init_time_from_py(item);
  if (ray_obj == NULL)
    return NULL;
  return raypy_wrap_ray_object(ray_obj);
}
PyObject *raypy_init_timestamp(PyObject *self, PyObject *args) {
  (void)self;
  CHECK_MAIN_THREAD();

  PyObject *item;
  if (!PyArg_ParseTuple(args, "O", &item))
    return NULL;

  obj_p ray_obj = raypy_init_timestamp_from_py(item);
  if (ray_obj == NULL)
    return NULL;
  return raypy_wrap_ray_object(ray_obj);
}
PyObject *raypy_init_guid(PyObject *self, PyObject *args) {
  (void)self;
  CHECK_MAIN_THREAD();

  PyObject *item;
  if (!PyArg_ParseTuple(args, "O", &item))
    return NULL;

  obj_p ray_obj = raypy_init_guid_from_py(item);
  if (ray_obj == NULL)
    return NULL;
  return raypy_wrap_ray_object(ray_obj);
}
PyObject *raypy_init_list(PyObject *self, PyObject *args) {
  (void)self;
  CHECK_MAIN_THREAD();

  PyObject *item;
  if (!PyArg_ParseTuple(args, "O", &item))
    return NULL;

  obj_p ray_obj = raypy_init_list_from_py(item);
  if (ray_obj == NULL) {
    return NULL;
  }
  return raypy_wrap_ray_object(ray_obj);
}
PyObject *raypy_init_table(PyObject *self, PyObject *args) {
  (void)self;
  CHECK_MAIN_THREAD();

  RayObject *keys_obj;
  RayObject *vals_obj;

  if (!PyArg_ParseTuple(args, "O!O!", &RayObjectType, &keys_obj, &RayObjectType,
                        &vals_obj))
    return NULL;

  obj_p ray_obj = ray_table(keys_obj->obj, vals_obj->obj);
  if (ray_obj == NULL) {
    PyErr_SetString(PyExc_MemoryError, "Failed to create table");
    return NULL;
  }
  return raypy_wrap_ray_object(ray_obj);
}
PyObject *raypy_init_dict(PyObject *self, PyObject *args) {
  (void)self;
  CHECK_MAIN_THREAD();

  RayObject *keys_obj;
  RayObject *vals_obj;

  if (!PyArg_ParseTuple(args, "O!O!", &RayObjectType, &keys_obj, &RayObjectType,
                        &vals_obj))
    return NULL;

  obj_p ray_obj = ray_dict(keys_obj->obj, vals_obj->obj);
  if (ray_obj == NULL) {
    PyErr_SetString(PyExc_RuntimeError, "Failed to create dictionary");
    return NULL;
  }
  return raypy_wrap_ray_object(ray_obj);
}

static obj_p convert_py_item_to_ray(PyObject *item,
                                    int type_code); // Forward declaration

static int fill_obj_from_py_sequence(obj_p *target_obj, PyObject *fill,
                                     int type_code, int is_vector,
                                     const char *error_msg) {
  Py_ssize_t len = PySequence_Size(fill);
  if (len < 0)
    return -1;

  for (Py_ssize_t i = 0; i < len; i++) {
    PyObject *item = PySequence_GetItem(fill, i);
    if (item == NULL)
      return -1;

    obj_p ray_item = convert_py_item_to_ray(item, type_code);
    Py_DECREF(item);

    if (ray_item == NULL && PyErr_Occurred()) {
      return -1;
    }
    if (ray_item == NULL) {
      PyErr_SetString(PyExc_TypeError, error_msg);
      return -1;
    }

    if (is_vector) {
      ins_obj(target_obj, (i64_t)i, ray_item);
    } else {
      push_obj(target_obj, ray_item);
    }
  }

  return 0;
}

PyObject *raypy_init_vector(PyObject *self, PyObject *args) {
  (void)self;
  CHECK_MAIN_THREAD();

  int type_code;
  PyObject *second_arg;
  if (!PyArg_ParseTuple(args, "iO", &type_code, &second_arg))
    return NULL;

  obj_p ray_obj = NULL;

  if (PyLong_Check(second_arg)) {
    Py_ssize_t length = PyLong_AsSsize_t(second_arg);
    if (length < 0 && PyErr_Occurred())
      return NULL;

    int vector_type_code = type_code < 0 ? -type_code : type_code;
    ray_obj = vector(vector_type_code, (u64_t)length);
    if (ray_obj == NULL) {
      PyErr_SetString(PyExc_MemoryError, "Failed to create vector");
      return NULL;
    }
  } else if (PySequence_Check(second_arg)) {
    Py_ssize_t len = PySequence_Size(second_arg);
    if (len < 0)
      return NULL;

    int vector_type_code = type_code < 0 ? -type_code : type_code;
    ray_obj = vector(vector_type_code, (u64_t)len);
    if (ray_obj == NULL) {
      PyErr_SetString(PyExc_MemoryError, "Failed to create vector");
      return NULL;
    }

    if (fill_obj_from_py_sequence(&ray_obj, second_arg, vector_type_code, 1,
                                  "Unsupported type code for bulk fill") < 0) {
      drop_obj(ray_obj);
      return NULL;
    }
  } else {
    PyErr_SetString(
        PyExc_TypeError,
        "Second argument must be an integer (length) or a sequence (items)");
    return NULL;
  }

  return raypy_wrap_ray_object(ray_obj);
}

// CONVERSION UTILS
obj_p raypy_init_i16_from_py(PyObject *item) {
  long val = PyLong_AsLong(item);
  if (val == -1 && PyErr_Occurred())
    return NULL;
  return i16((i16_t)val);
}
obj_p raypy_init_i32_from_py(PyObject *item) {
  long val = PyLong_AsLong(item);
  if (val == -1 && PyErr_Occurred())
    return NULL;
  return i32((i32_t)val);
}
obj_p raypy_init_i64_from_py(PyObject *item) {
  long long val = PyLong_AsLongLong(item);
  if (val == -1 && PyErr_Occurred())
    return NULL;
  return i64(val);
}
obj_p raypy_init_f64_from_py(PyObject *item) {
  double val = PyFloat_AsDouble(item);
  if (val == -1.0 && PyErr_Occurred())
    return NULL;
  return f64(val);
}
obj_p raypy_init_c8_from_py(PyObject *item) {
  Py_ssize_t str_len;
  const char *str_val = PyUnicode_AsUTF8AndSize(item, &str_len);
  if (str_val == NULL)
    return NULL;
  return c8(str_len > 0 ? str_val[0] : '\0');
}
obj_p raypy_init_string_from_py(PyObject *item) {
  Py_ssize_t str_len;
  const char *str_val = PyUnicode_AsUTF8AndSize(item, &str_len);
  if (str_val == NULL)
    return NULL;
  return string_from_str(str_val, str_len);
}
obj_p raypy_init_b8_from_py(PyObject *item) {
  int val = PyObject_IsTrue(item);
  if (val == -1)
    return NULL;
  return b8(val ? 1 : 0);
}
obj_p raypy_init_u8_from_py(PyObject *item) {
  long val = PyLong_AsLong(item);
  if (val == -1 && PyErr_Occurred())
    return NULL;
  return u8((unsigned char)val);
}
obj_p raypy_init_symbol_from_py(PyObject *item) {
  Py_ssize_t str_len;
  const char *str_val = PyUnicode_AsUTF8AndSize(item, &str_len);
  if (str_val == NULL)
    return NULL;
  return symbol(str_val, str_len);
}
obj_p raypy_init_guid_from_py(PyObject *item) {
  PyObject *guid_str_obj = NULL;

  if (PyUnicode_Check(item)) {
    Py_INCREF(item);
    guid_str_obj = item;
  } else {
    guid_str_obj = PyObject_Str(item);
    if (guid_str_obj == NULL)
      return NULL;
  }

  Py_ssize_t guid_len;
  const char *guid_str = PyUnicode_AsUTF8AndSize(guid_str_obj, &guid_len);
  if (guid_str == NULL) {
    Py_DECREF(guid_str_obj);
    return NULL;
  }

  obj_p ray_obj = vector(TYPE_I64, 2);
  if (!ray_obj) {
    Py_DECREF(guid_str_obj);
    PyErr_SetString(PyExc_MemoryError, "Failed to create GUID");
    return NULL;
  }

  ray_obj->type = -TYPE_GUID;
  if (guid_from_str(guid_str, guid_len, *AS_GUID(ray_obj)) != 0) {
    drop_obj(ray_obj);
    Py_DECREF(guid_str_obj);
    PyErr_SetString(PyExc_ValueError, "Invalid GUID format");
    return NULL;
  }

  Py_DECREF(guid_str_obj);
  return ray_obj;
}

obj_p raypy_init_date_from_py(PyObject *item) {
  PyObject *str_obj = PyObject_Str(item);
  if (str_obj == NULL)
    return NULL;

  obj_p ray_str = raypy_init_string_from_py(str_obj);
  Py_DECREF(str_obj);
  if (ray_str == NULL)
    return NULL;

  obj_p type_symbol = symbol("date", 4);
  if (type_symbol == NULL) {
    drop_obj(ray_str);
    return NULL;
  }

  obj_p quoted_symbol = ray_quote(type_symbol);
  drop_obj(type_symbol);
  if (quoted_symbol == NULL) {
    drop_obj(ray_str);
    return NULL;
  }

  obj_p date_obj = ray_cast_obj(quoted_symbol, ray_str);
  drop_obj(quoted_symbol);
  drop_obj(ray_str);

  if (date_obj == NULL) {
    PyErr_SetString(PyExc_ValueError, "Failed to cast to date");
    return NULL;
  }

  if (date_obj->i32 == -730120) {
    PyErr_SetString(PyExc_ValueError, "Failed to cast to date");
    drop_obj(date_obj);
    return NULL;
  }

  return date_obj;
}

obj_p raypy_init_time_from_py(PyObject *item) {
  PyObject *str_obj = PyObject_Str(item);
  if (str_obj == NULL)
    return NULL;

  obj_p ray_str = raypy_init_string_from_py(str_obj);
  Py_DECREF(str_obj);
  if (ray_str == NULL)
    return NULL;

  obj_p type_symbol = symbol("time", 4);
  if (type_symbol == NULL) {
    drop_obj(ray_str);
    return NULL;
  }

  obj_p quoted_symbol = ray_quote(type_symbol);
  drop_obj(type_symbol);
  if (quoted_symbol == NULL) {
    drop_obj(ray_str);
    return NULL;
  }

  obj_p time_obj = ray_cast_obj(quoted_symbol, ray_str);
  drop_obj(quoted_symbol);
  drop_obj(ray_str);

  if (time_obj == NULL) {
    PyErr_SetString(PyExc_ValueError, "Failed to cast to time");
    return NULL;
  }

  if (time_obj->i32 == NULL_I32) {
    PyErr_SetString(PyExc_ValueError, "Failed to cast to time");
    drop_obj(time_obj);
    return NULL;
  }

  return time_obj;
}

obj_p raypy_init_timestamp_from_py(PyObject *item) {
  PyObject *str_obj = PyObject_Str(item);
  if (str_obj == NULL)
    return NULL;

  obj_p ray_str = raypy_init_string_from_py(str_obj);
  Py_DECREF(str_obj);
  if (ray_str == NULL)
    return NULL;

  obj_p type_symbol = symbol("timestamp", 9);
  if (type_symbol == NULL) {
    drop_obj(ray_str);
    return NULL;
  }

  obj_p quoted_symbol = ray_quote(type_symbol);
  drop_obj(type_symbol);
  if (quoted_symbol == NULL) {
    drop_obj(ray_str);
    return NULL;
  }

  obj_p timestamp_obj = ray_cast_obj(quoted_symbol, ray_str);
  drop_obj(quoted_symbol);
  drop_obj(ray_str);

  if (timestamp_obj == NULL) {
    PyErr_SetString(PyExc_ValueError, "Failed to cast to timestamp");
    return NULL;
  }

  if (timestamp_obj->i64 == NULL_I64) {
    PyErr_SetString(PyExc_ValueError, "Failed to cast to timestamp");
    drop_obj(timestamp_obj);
    return NULL;
  }

  return timestamp_obj;
}

obj_p raypy_init_dict_from_py(PyObject *item) {
  if (!PyDict_Check(item))
    return NULL;

  Py_ssize_t dict_size = PyDict_Size(item);
  if (dict_size < 0)
    return NULL;

  obj_p dict_keys = vector(TYPE_SYMBOL, (u64_t)dict_size);
  if (!dict_keys)
    return NULL;

  PyObject *py_dict_values = PyList_New(dict_size);
  if (!py_dict_values) {
    drop_obj(dict_keys);
    return NULL;
  }

  PyObject *key, *val;
  Py_ssize_t pos = 0;
  Py_ssize_t idx = 0;

  while (PyDict_Next(item, &pos, &key, &val)) {
    obj_p ray_key = raypy_init_symbol_from_py(key);
    if (!ray_key) {
      Py_DECREF(py_dict_values);
      drop_obj(dict_keys);
      return NULL;
    }
    ins_obj(&dict_keys, (i64_t)idx, ray_key);
    PyList_SET_ITEM(py_dict_values, idx, val);
    Py_INCREF(val);
    idx++;
  }

  obj_p dict_values = raypy_init_list_from_py(py_dict_values);
  Py_DECREF(py_dict_values);
  if (!dict_values) {
    drop_obj(dict_values);
    return NULL;
  }

  obj_p result = ray_dict(dict_keys, dict_values);
  if (!result) {
    drop_obj(dict_keys);
    drop_obj(dict_values);
    return NULL;
  }

  return result;
}

obj_p raypy_init_list_from_py(PyObject *item) {
  if (!PyList_Check(item) && !PyTuple_Check(item))
    return NULL;

  obj_p list_vec = vector(TYPE_LIST, 0);
  if (!list_vec)
    return NULL;

  if (fill_obj_from_py_sequence(&list_vec, item, 0, 0,
                                "Unsupported type for List item") < 0) {
    drop_obj(list_vec);
    return NULL;
  }

  return list_vec;
}

static obj_p convert_py_item_to_ray(PyObject *item, int type_code) {
  if (item == Py_None) {
    return NULL_OBJ;
  }

  if (PyObject_TypeCheck(item, &RayObjectType)) {
    RayObject *ray_obj = (RayObject *)item;
    if (ray_obj->obj != NULL) {
      return clone_obj(ray_obj->obj);
    }
    return NULL;
  }

  if (PyObject_HasAttrString(item, "ptr")) {
    PyObject *ptr_attr = PyObject_GetAttrString(item, "ptr");
    if (ptr_attr != NULL && PyObject_TypeCheck(ptr_attr, &RayObjectType)) {
      RayObject *ray_obj = (RayObject *)ptr_attr;
      if (ray_obj->obj != NULL) {
        obj_p result = clone_obj(ray_obj->obj);
        Py_XDECREF(ptr_attr);
        return result;
      }
    }
    Py_XDECREF(ptr_attr);
  }

  int abs_type_code = type_code < 0 ? -type_code : type_code;
  if (abs_type_code > 0) {
    if (abs_type_code == TYPE_I16) {
      return raypy_init_i16_from_py(item);
    } else if (abs_type_code == TYPE_I32) {
      return raypy_init_i32_from_py(item);
    } else if (abs_type_code == TYPE_I64) {
      return raypy_init_i64_from_py(item);
    } else if (abs_type_code == TYPE_F64) {
      return raypy_init_f64_from_py(item);
    } else if (abs_type_code == TYPE_B8) {
      return raypy_init_b8_from_py(item);
    } else if (abs_type_code == TYPE_SYMBOL) {
      return raypy_init_symbol_from_py(item);
    } else if (abs_type_code == TYPE_U8) {
      return raypy_init_u8_from_py(item);
    } else if (abs_type_code == TYPE_C8) {
      return raypy_init_c8_from_py(item);
    } else if (abs_type_code == TYPE_GUID) {
      return raypy_init_guid_from_py(item);
    } else if (abs_type_code == TYPE_DATE) {
      return raypy_init_date_from_py(item);
    } else if (abs_type_code == TYPE_TIME) {
      return raypy_init_time_from_py(item);
    } else if (abs_type_code == TYPE_TIMESTAMP) {
      return raypy_init_timestamp_from_py(item);
    }
    return NULL;
  }

  // Auto-detect type
  if (PyBool_Check(item)) {
    return raypy_init_b8_from_py(item);
  } else if (PyLong_Check(item)) {
    return raypy_init_i64_from_py(item);
  } else if (PyFloat_Check(item)) {
    return raypy_init_f64_from_py(item);
  } else if (PyUnicode_Check(item) || PyBytes_Check(item)) {
    return raypy_init_symbol_from_py(item);
  } else if (PyDict_Check(item)) {
    return raypy_init_dict_from_py(item);
  } else if (PyList_Check(item) || PyTuple_Check(item)) {
    return raypy_init_list_from_py(item);
  } else {
    PyObject *type_obj = (PyObject *)Py_TYPE(item);
    PyObject *type_name = PyObject_GetAttrString(type_obj, "__name__");
    if (type_name != NULL) {
      const char *name_str = PyUnicode_AsUTF8(type_name);
      if (name_str != NULL) {
        obj_p result = NULL;
        if (strcmp(name_str, "date") == 0) {
          result = raypy_init_date_from_py(item);
        } else if (strcmp(name_str, "time") == 0) {
          result = raypy_init_time_from_py(item);
        } else if (strcmp(name_str, "datetime") == 0) {
          result = raypy_init_timestamp_from_py(item);
        }
        Py_DECREF(type_name);
        return result;
      }
      Py_DECREF(type_name);
    }
  }

  return NULL;
}
