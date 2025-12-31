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
PyObject *raypy_init_vector(PyObject *self, PyObject *args) {
  (void)self;
  CHECK_MAIN_THREAD();
  int type_code;
  Py_ssize_t length;

  if (!PyArg_ParseTuple(args, "in", &type_code, &length))
    return NULL;

  obj_p ray_obj = vector(type_code, (u64_t)length);
  if (ray_obj == NULL) {
    PyErr_SetString(PyExc_MemoryError, "Failed to create vector");
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

  // Cast string to timestamp using ray_cast_obj
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

  // Create keys vector (SYMBOL type)
  obj_p keys_vec = vector(TYPE_SYMBOL, (u64_t)dict_size);
  if (!keys_vec)
    return NULL;

  // Create values vector (LIST type)
  obj_p vals_vec = vector(TYPE_LIST, (u64_t)dict_size);
  if (!vals_vec) {
    drop_obj(keys_vec);
    return NULL;
  }

  PyObject *key, *val;
  Py_ssize_t pos = 0;
  Py_ssize_t idx = 0;

  while (PyDict_Next(item, &pos, &key, &val)) {
    // Convert key to SYMBOL
    obj_p ray_key = raypy_init_symbol_from_py(key);
    if (!ray_key) {
      drop_obj(keys_vec);
      drop_obj(vals_vec);
      return NULL;
    }
    ins_obj(&keys_vec, (i64_t)idx, ray_key);

    // Convert value recursively
    obj_p ray_val = NULL;

    if (val == Py_None) {
      ray_val = NULL_OBJ;
    } else if (PyObject_TypeCheck(val, &RayObjectType)) {
      RayObject *ray_obj = (RayObject *)val;
      if (ray_obj->obj != NULL) {
        ray_val = clone_obj(ray_obj->obj);
      }
    } else if (PyObject_HasAttrString(val, "ptr")) {
      PyObject *ptr_attr = PyObject_GetAttrString(val, "ptr");
      if (ptr_attr != NULL && PyObject_TypeCheck(ptr_attr, &RayObjectType)) {
        RayObject *ray_obj = (RayObject *)ptr_attr;
        if (ray_obj->obj != NULL) {
          ray_val = clone_obj(ray_obj->obj);
        }
      }
      Py_XDECREF(ptr_attr);
    } else if (PyBool_Check(val)) {
      ray_val = raypy_init_b8_from_py(val);
    } else if (PyLong_Check(val)) {
      ray_val = raypy_init_i64_from_py(val);
    } else if (PyFloat_Check(val)) {
      ray_val = raypy_init_f64_from_py(val);
    } else if (PyUnicode_Check(val) || PyBytes_Check(val)) {
      ray_val = raypy_init_symbol_from_py(val);
    } else if (PyDict_Check(val)) {
      ray_val = raypy_init_dict_from_py(val);
    } else if (PyList_Check(val) || PyTuple_Check(val)) {
      ray_val = raypy_init_list_from_py(val);
    } else {
      PyObject *type_obj = (PyObject *)Py_TYPE(val);
      PyObject *type_name = PyObject_GetAttrString(type_obj, "__name__");
      if (type_name != NULL) {
        const char *name_str = PyUnicode_AsUTF8(type_name);
        if (name_str != NULL) {
          if (strcmp(name_str, "date") == 0) {
            ray_val = raypy_init_date_from_py(val);
          } else if (strcmp(name_str, "time") == 0) {
            ray_val = raypy_init_time_from_py(val);
          } else if (strcmp(name_str, "datetime") == 0) {
            ray_val = raypy_init_timestamp_from_py(val);
          }
        }
        Py_DECREF(type_name);
      }
    }

    if (!ray_val) {
      drop_obj(keys_vec);
      drop_obj(vals_vec);
      return NULL;
    }
    ins_obj(&vals_vec, (i64_t)idx, ray_val);
    idx++;
  }

  obj_p result = ray_dict(keys_vec, vals_vec);
  if (!result) {
    drop_obj(keys_vec);
    drop_obj(vals_vec);
    return NULL;
  }

  return result;
}

obj_p raypy_init_list_from_py(PyObject *item) {
  if (!PyList_Check(item) && !PyTuple_Check(item))
    return NULL;

  Py_ssize_t len = PySequence_Size(item);
  if (len < 0)
    return NULL;

  obj_p list_vec = vector(TYPE_LIST, (u64_t)len);
  if (!list_vec)
    return NULL;

  for (Py_ssize_t i = 0; i < len; i++) {
    PyObject *list_item = PySequence_GetItem(item, i);
    if (!list_item) {
      drop_obj(list_vec);
      return NULL;
    }

    obj_p ray_item = NULL;

    if (list_item == Py_None) {
      ray_item = NULL_OBJ;
    } else if (PyObject_TypeCheck(list_item, &RayObjectType)) {
      RayObject *ray_obj = (RayObject *)list_item;
      if (ray_obj->obj != NULL) {
        ray_item = clone_obj(ray_obj->obj);
      }
    } else if (PyObject_HasAttrString(list_item, "ptr")) {
      PyObject *ptr_attr = PyObject_GetAttrString(list_item, "ptr");
      if (ptr_attr != NULL && PyObject_TypeCheck(ptr_attr, &RayObjectType)) {
        RayObject *ray_obj = (RayObject *)ptr_attr;
        if (ray_obj->obj != NULL) {
          ray_item = clone_obj(ray_obj->obj);
        }
      }
      Py_XDECREF(ptr_attr);
    } else if (PyBool_Check(list_item)) {
      ray_item = raypy_init_b8_from_py(list_item);
    } else if (PyLong_Check(list_item)) {
      ray_item = raypy_init_i64_from_py(list_item);
    } else if (PyFloat_Check(list_item)) {
      ray_item = raypy_init_f64_from_py(list_item);
    } else if (PyUnicode_Check(list_item) || PyBytes_Check(list_item)) {
      ray_item = raypy_init_symbol_from_py(list_item);
    } else if (PyDict_Check(list_item)) {
      ray_item = raypy_init_dict_from_py(list_item);
    } else if (PyList_Check(list_item) || PyTuple_Check(list_item)) {
      ray_item = raypy_init_list_from_py(list_item);
    } else {
      PyObject *type_obj = (PyObject *)Py_TYPE(list_item);
      PyObject *type_name = PyObject_GetAttrString(type_obj, "__name__");
      if (type_name != NULL) {
        const char *name_str = PyUnicode_AsUTF8(type_name);
        if (name_str != NULL) {
          if (strcmp(name_str, "date") == 0) {
            ray_item = raypy_init_date_from_py(list_item);
          } else if (strcmp(name_str, "time") == 0) {
            ray_item = raypy_init_time_from_py(list_item);
          } else if (strcmp(name_str, "datetime") == 0) {
            ray_item = raypy_init_timestamp_from_py(list_item);
          }
        }
        Py_DECREF(type_name);
      }
    }

    Py_DECREF(list_item);

    if (!ray_item) {
      drop_obj(list_vec);
      return NULL;
    }

    ins_obj(&list_vec, (i64_t)i, ray_item);
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

  // If type_code is specified (for vectors), use type-specific conversion
  if (type_code > 0) {
    if (type_code == TYPE_I16) {
      return raypy_init_i16_from_py(item);
    } else if (type_code == TYPE_I32) {
      return raypy_init_i32_from_py(item);
    } else if (type_code == TYPE_I64) {
      return raypy_init_i64_from_py(item);
    } else if (type_code == TYPE_F64) {
      return raypy_init_f64_from_py(item);
    } else if (type_code == TYPE_B8) {
      return raypy_init_b8_from_py(item);
    } else if (type_code == TYPE_SYMBOL) {
      return raypy_init_symbol_from_py(item);
    } else if (type_code == TYPE_U8) {
      return raypy_init_u8_from_py(item);
    } else if (type_code == TYPE_C8) {
      return raypy_init_c8_from_py(item);
    } else if (type_code == TYPE_GUID) {
      return raypy_init_guid_from_py(item);
    } else if (type_code == TYPE_DATE) {
      return raypy_init_date_from_py(item);
    } else if (type_code == TYPE_TIME) {
      return raypy_init_time_from_py(item);
    } else if (type_code == TYPE_TIMESTAMP) {
      return raypy_init_timestamp_from_py(item);
    }
    return NULL; // Unsupported type code
  }

  // Auto-detect type (for lists)
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

// Unified function to fill iterables (vectors or lists)
// For vectors: use ins_obj with index (vectors have fixed length)
// For lists: use push_obj (lists grow dynamically)
static PyObject *fill_iterable_impl(RayObject *iter_obj, PyObject *fill,
                                    int type_code, int is_vector,
                                    const char *error_msg) {
  Py_ssize_t len = PySequence_Size(fill);
  if (len < 0)
    return NULL;

  for (Py_ssize_t i = 0; i < len; i++) {
    PyObject *item = PySequence_GetItem(fill, i);
    if (item == NULL)
      return NULL;

    obj_p ray_item = convert_py_item_to_ray(item, type_code);
    Py_DECREF(item);

    if (ray_item == NULL && PyErr_Occurred()) {
      return NULL;
    }
    if (ray_item == NULL) {
      PyErr_SetString(PyExc_TypeError, error_msg);
      return NULL;
    }

    if (is_vector) {
      // Vectors have fixed length, insert at specific index
      ins_obj(&iter_obj->obj, (i64_t)i, ray_item);
    } else {
      // Lists grow dynamically, append to end
      push_obj(&iter_obj->obj, ray_item);
    }
  }

  Py_RETURN_NONE;
}

PyObject *raypy_fill_vector(PyObject *self UNUSED_SELF_PARAM, PyObject *args) {
  CHECK_MAIN_THREAD();
  RayObject *vec_obj;
  PyObject *fill;

  if (!PyArg_ParseTuple(args, "O!O", &RayObjectType, &vec_obj, &fill))
    return NULL;

  int type_code = vec_obj->obj->type;
  return fill_iterable_impl(vec_obj, fill, type_code, 1,
                            "Unsupported type code for bulk fill");
}

PyObject *raypy_fill_list(PyObject *self UNUSED_SELF_PARAM, PyObject *args) {
  CHECK_MAIN_THREAD();
  RayObject *list_obj;
  PyObject *fill;

  if (!PyArg_ParseTuple(args, "O!O", &RayObjectType, &list_obj, &fill))
    return NULL;

  if (list_obj->obj == NULL || list_obj->obj->type != TYPE_LIST) {
    PyErr_SetString(PyExc_TypeError, "Object is not a LIST type");
    return NULL;
  }

  return fill_iterable_impl(list_obj, fill, 0, 0,
                            "Unsupported type for List item");
}
