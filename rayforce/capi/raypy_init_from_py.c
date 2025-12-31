#include "rayforce_c.h"

PyObject *raypy_init_i16(PyObject *self, PyObject *args) {
  (void)self;
  CHECK_MAIN_THREAD();

  PyObject *item;
  if (!PyArg_ParseTuple(args, "O", &item))
    return NULL;

  return raypy_wrap_ray_object(raypy_init_i16_from_py(item));
}
PyObject *raypy_init_i32(PyObject *self, PyObject *args) {
  (void)self;
  CHECK_MAIN_THREAD();

  PyObject *item;
  if (!PyArg_ParseTuple(args, "O", &item))
    return NULL;

  return raypy_wrap_ray_object(raypy_init_i32_from_py(item));
}
PyObject *raypy_init_i64(PyObject *self, PyObject *args) {
  (void)self;
  CHECK_MAIN_THREAD();

  PyObject *item;
  if (!PyArg_ParseTuple(args, "O", &item))
    return NULL;

  return raypy_wrap_ray_object(raypy_init_i64_from_py(item));
}
PyObject *raypy_init_f64(PyObject *self, PyObject *args) {
  (void)self;
  CHECK_MAIN_THREAD();

  PyObject *item;
  if (!PyArg_ParseTuple(args, "O", &item))
    return NULL;

  return raypy_wrap_ray_object(raypy_init_f64_from_py(item));
}
PyObject *raypy_init_c8(PyObject *self, PyObject *args) {
  (void)self;
  CHECK_MAIN_THREAD();

  PyObject *item;
  if (!PyArg_ParseTuple(args, "O", &item))
    return NULL;

  return raypy_wrap_ray_object(raypy_init_c8_from_py(item));
}
PyObject *raypy_init_string(PyObject *self, PyObject *args) {
  (void)self;
  CHECK_MAIN_THREAD();

  const char *value;
  Py_ssize_t len;
  if (!PyArg_ParseTuple(args, "s#", &value, &len))
    return NULL;

  obj_p ray_obj = string_from_str(value, len);
  if (ray_obj == NULL) {
    PyErr_SetString(PyExc_MemoryError, "Failed to create string");
    return NULL;
  }
  return raypy_wrap_ray_object(ray_obj);
}
PyObject *raypy_init_symbol(PyObject *self, PyObject *args) {
  (void)self;
  CHECK_MAIN_THREAD();

  PyObject *item;
  if (!PyArg_ParseTuple(args, "O", &item))
    return NULL;

  return raypy_wrap_ray_object(raypy_init_symbol_from_py(item));
}
PyObject *raypy_init_b8(PyObject *self, PyObject *args) {
  (void)self;
  CHECK_MAIN_THREAD();

  PyObject *item;
  if (!PyArg_ParseTuple(args, "O", &item))
    return NULL;

  return raypy_wrap_ray_object(raypy_init_b8_from_py(item));
}
PyObject *raypy_init_u8(PyObject *self, PyObject *args) {
  (void)self;
  CHECK_MAIN_THREAD();

  PyObject *item;
  if (!PyArg_ParseTuple(args, "O", &item))
    return NULL;

  return raypy_wrap_ray_object(raypy_init_u8_from_py(item));
}
PyObject *raypy_init_date(PyObject *self, PyObject *args) {
  (void)self;
  CHECK_MAIN_THREAD();

  PyObject *item;
  if (!PyArg_ParseTuple(args, "O", &item))
    return NULL;

  return raypy_wrap_ray_object(raypy_init_date_from_py(item));
}
PyObject *raypy_init_time(PyObject *self, PyObject *args) {
  (void)self;
  CHECK_MAIN_THREAD();

  PyObject *item;
  if (!PyArg_ParseTuple(args, "O", &item))
    return NULL;

  return raypy_wrap_ray_object(raypy_init_time_from_py(item));
}
PyObject *raypy_init_timestamp(PyObject *self, PyObject *args) {
  (void)self;
  CHECK_MAIN_THREAD();

  PyObject *item;
  if (!PyArg_ParseTuple(args, "O", &item))
    return NULL;

  return raypy_wrap_ray_object(raypy_init_timestamp_from_py(item));
}
PyObject *raypy_init_guid(PyObject *self, PyObject *args) {
  (void)self;
  CHECK_MAIN_THREAD();

  PyObject *item;
  if (!PyArg_ParseTuple(args, "O", &item))
    return NULL;

  return raypy_wrap_ray_object(raypy_init_guid_from_py(item));
}
PyObject *raypy_init_list(PyObject *self, PyObject *args) {
  (void)self;
  CHECK_MAIN_THREAD();

  Py_ssize_t initial_size = 0;
  if (!PyArg_ParseTuple(args, "|n", &initial_size))
    return NULL;

  obj_p ray_obj = vector(TYPE_LIST, (u64_t)initial_size);
  if (ray_obj == NULL) {
    PyErr_SetString(PyExc_MemoryError, "Failed to create list");
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
  const char *str_val;
  Py_ssize_t str_len;
  if (PyUnicode_Check(item)) {
    str_val = PyUnicode_AsUTF8AndSize(item, &str_len);
    if (str_val == NULL)
      return NULL;
  } else if (PyBytes_Check(item)) {
    str_val = PyBytes_AsString(item);
    if (str_val == NULL)
      return NULL;
    str_len = PyBytes_Size(item);
  } else {
    PyErr_SetString(PyExc_TypeError, "Expected string or bytes for C8");
    return NULL;
  }
  if (str_len != 1) {
    PyErr_SetString(PyExc_ValueError, "Character must be a single character");
    return NULL;
  }
  return c8(str_val[0]);
}
obj_p raypy_init_b8_from_py(PyObject *item) {
  int val = PyObject_IsTrue(item);
  if (val == -1)
    return NULL;
  return b8(val ? 1 : 0);
}
obj_p raypy_init_symbol_from_py(PyObject *item) {
  const char *str_val;
  Py_ssize_t str_len;

  if (PyUnicode_Check(item)) {
    str_val = PyUnicode_AsUTF8AndSize(item, &str_len);
    if (str_val == NULL)
      return NULL;
  } else if (PyBytes_Check(item)) {
    str_val = PyBytes_AsString(item);
    if (str_val == NULL)
      return NULL;
    str_len = PyBytes_Size(item);
  } else {
    PyErr_SetString(PyExc_TypeError, "Expected string or bytes for SYMBOL");
    return NULL;
  }

  return symbol(str_val, str_len);
}

obj_p raypy_init_guid_from_py(PyObject *item) {
  PyObject *uuid_module = NULL, *uuid_class = NULL;
  PyObject *uuid_obj = NULL, *uuid_str = NULL;
  const char *guid_str = NULL;
  Py_ssize_t guid_len = 0;

  uuid_module = PyImport_ImportModule("uuid");
  if (!uuid_module)
    return NULL;

  uuid_class = PyObject_GetAttrString(uuid_module, "UUID");
  Py_DECREF(uuid_module);
  if (!uuid_class)
    return NULL;

  int is_uuid_instance = PyObject_IsInstance(item, uuid_class);
  if (is_uuid_instance == 1) {
    Py_INCREF(item);
    uuid_obj = item;
  } else if (PyBytes_Check(item)) {
    Py_ssize_t n = PyBytes_Size(item);
    if (n < 0) {
      Py_DECREF(uuid_class);
      return NULL;
    }

    if (n == 16) {
      PyObject *kwargs = Py_BuildValue("{s:O}", "bytes", item);
      if (!kwargs) {
        Py_DECREF(uuid_class);
        return NULL;
      }

      PyObject *empty_args = PyTuple_New(0);
      if (!empty_args) {
        Py_DECREF(kwargs);
        Py_DECREF(uuid_class);
        return NULL;
      }

      uuid_obj = PyObject_Call(uuid_class, empty_args, kwargs);
      Py_DECREF(empty_args);
      Py_DECREF(kwargs);
    } else {
      PyObject *s = PyUnicode_DecodeUTF8(
          PyBytes_AS_STRING(item), n,
          "strict"); // treat as textual bytes (UUID string)
      if (!s) {
        Py_DECREF(uuid_class);
        return NULL;
      }
      uuid_obj = PyObject_CallFunctionObjArgs(uuid_class, s, NULL);
      Py_DECREF(s);
    }
  } else {
    uuid_obj = PyObject_CallFunctionObjArgs(uuid_class, item, NULL);
  }

  Py_DECREF(uuid_class);
  if (!uuid_obj)
    return NULL;

  uuid_str = PyObject_Str(uuid_obj);
  Py_DECREF(uuid_obj);
  if (!uuid_str)
    return NULL;

  guid_str = PyUnicode_AsUTF8AndSize(uuid_str, &guid_len);
  if (!guid_str) {
    Py_DECREF(uuid_str);
    return NULL;
  }

  obj_p result = vector(TYPE_I64, 2);
  if (!result) {
    Py_DECREF(uuid_str);
    PyErr_SetString(PyExc_MemoryError, "Failed to create GUID");
    return NULL;
  }

  result->type = -TYPE_GUID;
  if (guid_from_str(guid_str, guid_len, *AS_GUID(result)) != 0) {
    drop_obj(result);
    Py_DECREF(uuid_str);
    PyErr_SetString(PyExc_ValueError, "Invalid GUID format");
    return NULL;
  }

  Py_DECREF(uuid_str);
  return result;
}

obj_p raypy_init_u8_from_py(PyObject *item) {
  long val = PyLong_AsLong(item);
  if (val == -1 && PyErr_Occurred())
    return NULL;
  return u8((unsigned char)val);
}

obj_p raypy_init_date_from_py(PyObject *item) {
  long days_val;

  if (PyUnicode_Check(item)) {
    PyObject *datetime_module = PyImport_ImportModule("datetime");
    if (!datetime_module)
      return NULL;

    PyObject *date_class = PyObject_GetAttrString(datetime_module, "date");
    Py_DECREF(datetime_module);
    if (!date_class)
      return NULL;

    PyObject *fromiso = PyObject_GetAttrString(date_class, "fromisoformat");
    Py_DECREF(date_class);
    if (!fromiso)
      return NULL;

    PyObject *date_obj = PyObject_CallFunctionObjArgs(fromiso, item, NULL);
    Py_DECREF(fromiso);
    if (!date_obj)
      return NULL;

    obj_p result = raypy_init_date_from_py(date_obj);
    Py_DECREF(date_obj);
    return result;
  }

  PyObject *type_obj = (PyObject *)Py_TYPE(item);
  PyObject *type_name = PyObject_GetAttrString(type_obj, "__name__");
  if (type_name != NULL) {
    const char *name_str = PyUnicode_AsUTF8(type_name);
    if (name_str != NULL && strcmp(name_str, "date") == 0) {
      PyObject *datetime_module = PyImport_ImportModule("datetime");
      if (!datetime_module) {
        Py_DECREF(type_name);
        return NULL;
      }
      PyObject *date_class = PyObject_GetAttrString(datetime_module, "date");
      Py_DECREF(datetime_module);
      if (!date_class) {
        Py_DECREF(type_name);
        return NULL;
      }
      PyObject *epoch_args = Py_BuildValue("(iii)", 2000, 1, 1);
      if (!epoch_args) {
        Py_DECREF(date_class);
        Py_DECREF(type_name);
        return NULL;
      }
      PyObject *epoch = PyObject_CallObject(date_class, epoch_args);
      Py_DECREF(epoch_args);
      Py_DECREF(date_class);
      if (!epoch) {
        Py_DECREF(type_name);
        return NULL;
      }
      PyObject *delta = PyNumber_Subtract(item, epoch); // (item - epoch).days
      Py_DECREF(epoch);
      if (!delta) {
        Py_DECREF(type_name);
        return NULL;
      }
      PyObject *days_attr = PyObject_GetAttrString(delta, "days");
      Py_DECREF(delta);
      if (!days_attr) {
        Py_DECREF(type_name);
        return NULL;
      }
      days_val = (long)PyLong_AsLong(days_attr);
      Py_DECREF(days_attr);
      if (days_val == -1 && PyErr_Occurred()) {
        Py_DECREF(type_name);
        return NULL;
      }
      Py_DECREF(type_name);
      return adate((int)days_val);
    }
    Py_DECREF(type_name);
  }

  days_val = PyLong_AsLong(item); // days since epoch
  if (days_val == -1 && PyErr_Occurred())
    return NULL;

  return adate((int)days_val);
}

obj_p raypy_init_time_from_py(PyObject *item) {
  int ms_val;

  if (PyUnicode_Check(item)) {
    PyObject *datetime_module = PyImport_ImportModule("datetime");
    if (!datetime_module)
      return NULL;

    PyObject *time_class = PyObject_GetAttrString(datetime_module, "time");
    Py_DECREF(datetime_module);
    if (!time_class)
      return NULL;

    PyObject *fromiso = PyObject_GetAttrString(time_class, "fromisoformat");
    Py_DECREF(time_class);
    if (!fromiso)
      return NULL;

    PyObject *time_obj = PyObject_CallFunctionObjArgs(fromiso, item, NULL);
    Py_DECREF(fromiso);
    if (!time_obj)
      return NULL;

    obj_p result = raypy_init_time_from_py(time_obj);
    Py_DECREF(time_obj);
    return result;
  }

  PyObject *type_obj = (PyObject *)Py_TYPE(item);
  PyObject *type_name = PyObject_GetAttrString(type_obj, "__name__");
  if (type_name != NULL) {
    const char *name_str = PyUnicode_AsUTF8(type_name);
    if (name_str != NULL && strcmp(name_str, "time") == 0) {
      // hour * 3600000 + minute * 60000 + second * 1000 + microsecond // 1000
      PyObject *hour_obj = PyObject_GetAttrString(item, "hour");
      PyObject *minute_obj = PyObject_GetAttrString(item, "minute");
      PyObject *second_obj = PyObject_GetAttrString(item, "second");
      PyObject *microsecond_obj = PyObject_GetAttrString(item, "microsecond");
      if (hour_obj == NULL || minute_obj == NULL || second_obj == NULL ||
          microsecond_obj == NULL) {
        Py_XDECREF(hour_obj);
        Py_XDECREF(minute_obj);
        Py_XDECREF(second_obj);
        Py_XDECREF(microsecond_obj);
        Py_DECREF(type_name);
        return NULL;
      }
      long hour = PyLong_AsLong(hour_obj);
      long minute = PyLong_AsLong(minute_obj);
      long second = PyLong_AsLong(second_obj);
      long microsecond = PyLong_AsLong(microsecond_obj);
      Py_DECREF(hour_obj);
      Py_DECREF(minute_obj);
      Py_DECREF(second_obj);
      Py_DECREF(microsecond_obj);
      if (hour == -1 || minute == -1 || second == -1 || microsecond == -1) {
        if (PyErr_Occurred()) {
          Py_DECREF(type_name);
          return NULL;
        }
      }
      ms_val = (int)(hour * 3600000 + minute * 60000 + second * 1000 +
                     microsecond / 1000);
      Py_DECREF(type_name);
    } else {
      Py_DECREF(type_name);
      long val = PyLong_AsLong(item); // milliseconds since midnight
      if (val == -1 && PyErr_Occurred())
        return NULL;
      ms_val = (int)val;
    }
  } else {
    long val = PyLong_AsLong(item); // milliseconds since midnight
    if (val == -1 && PyErr_Occurred())
      return NULL;
    ms_val = (int)val;
  }
  return atime(ms_val);
}

obj_p raypy_init_timestamp_from_py(PyObject *item) {
  long long ns_val;

  if (PyUnicode_Check(item)) {
    PyObject *datetime_module = PyImport_ImportModule("datetime");
    if (!datetime_module)
      return NULL;

    PyObject *datetime_class =
        PyObject_GetAttrString(datetime_module, "datetime");
    Py_DECREF(datetime_module);
    if (!datetime_class)
      return NULL;

    PyObject *fromiso = PyObject_GetAttrString(datetime_class, "fromisoformat");
    Py_DECREF(datetime_class);
    if (!fromiso)
      return NULL;

    PyObject *dt_obj = PyObject_CallFunctionObjArgs(fromiso, item, NULL);
    Py_DECREF(fromiso);
    if (!dt_obj)
      return NULL;

    obj_p result = raypy_init_timestamp_from_py(dt_obj);
    Py_DECREF(dt_obj);
    return result;
  }

  PyObject *type_obj = (PyObject *)Py_TYPE(item);
  PyObject *type_name = PyObject_GetAttrString(type_obj, "__name__");
  if (type_name != NULL) {
    const char *name_str = PyUnicode_AsUTF8(type_name);
    if (name_str != NULL && strcmp(name_str, "datetime") == 0) {
      PyObject *datetime_module = PyImport_ImportModule("datetime");
      if (!datetime_module) {
        Py_DECREF(type_name);
        return NULL;
      }
      PyObject *datetime_class =
          PyObject_GetAttrString(datetime_module, "datetime");
      PyObject *utc_obj = PyObject_GetAttrString(datetime_module, "UTC");
      Py_DECREF(datetime_module);
      if (!datetime_class || !utc_obj) {
        Py_XDECREF(datetime_class);
        Py_XDECREF(utc_obj);
        Py_DECREF(type_name);
        return NULL;
      }
      PyObject *epoch_args = Py_BuildValue("(iii)", 2000, 1, 1);
      if (!epoch_args) {
        Py_XDECREF(datetime_class);
        Py_XDECREF(utc_obj);
        Py_DECREF(type_name);
        return NULL;
      }
      PyObject *epoch_kwargs = Py_BuildValue("{s:O}", "tzinfo", utc_obj);
      Py_DECREF(utc_obj);
      if (!epoch_kwargs) {
        Py_DECREF(epoch_args);
        Py_XDECREF(datetime_class);
        Py_DECREF(type_name);
        return NULL;
      }
      PyObject *epoch = PyObject_Call(datetime_class, epoch_args, epoch_kwargs);
      Py_DECREF(epoch_args);
      Py_DECREF(epoch_kwargs);
      Py_DECREF(datetime_class);
      if (!epoch) {
        Py_DECREF(type_name);
        return NULL;
      }
      PyObject *item_tzinfo = PyObject_GetAttrString(item, "tzinfo");
      PyObject *item_to_use = item;
      if (!item_tzinfo) {
        Py_DECREF(epoch);
        Py_DECREF(type_name);
        return NULL;
      }
      if (item_tzinfo == Py_None) {
        Py_DECREF(item_tzinfo);
        PyObject *replace_method = PyObject_GetAttrString(item, "replace");
        if (!replace_method) {
          Py_DECREF(epoch);
          Py_DECREF(type_name);
          return NULL;
        }
        PyObject *utc_module = PyImport_ImportModule("datetime");
        PyObject *utc_tz = PyObject_GetAttrString(utc_module, "UTC");
        Py_DECREF(utc_module);
        if (!utc_tz) {
          Py_DECREF(replace_method);
          Py_DECREF(epoch);
          Py_DECREF(type_name);
          return NULL;
        }
        PyObject *replace_kwargs = Py_BuildValue("{s:O}", "tzinfo", utc_tz);
        Py_DECREF(utc_tz);
        if (!replace_kwargs) {
          Py_DECREF(replace_method);
          Py_DECREF(epoch);
          Py_DECREF(type_name);
          return NULL;
        }
        item_to_use =
            PyObject_Call(replace_method, PyTuple_New(0), replace_kwargs);
        Py_DECREF(replace_method);
        Py_DECREF(replace_kwargs);
        if (!item_to_use) {
          Py_DECREF(epoch);
          Py_DECREF(type_name);
          return NULL;
        }
      } else {
        Py_DECREF(item_tzinfo);
      }
      PyObject *delta =
          PyNumber_Subtract(item_to_use, epoch); // (item_to_use - epoch)
      if (item_to_use != item) {
        Py_DECREF(item_to_use);
      }
      Py_DECREF(epoch);
      if (!delta) {
        Py_DECREF(type_name);
        return NULL;
      }
      PyObject *days_attr = PyObject_GetAttrString(delta, "days");
      PyObject *seconds_attr = PyObject_GetAttrString(delta, "seconds");
      PyObject *microseconds_attr =
          PyObject_GetAttrString(delta, "microseconds");
      Py_DECREF(delta);
      if (!days_attr || !seconds_attr || !microseconds_attr) {
        Py_XDECREF(days_attr);
        Py_XDECREF(seconds_attr);
        Py_XDECREF(microseconds_attr);
        Py_DECREF(type_name);
        return NULL;
      }
      long days = PyLong_AsLong(days_attr);
      long seconds = PyLong_AsLong(seconds_attr);
      long microseconds = PyLong_AsLong(microseconds_attr);
      Py_DECREF(days_attr);
      Py_DECREF(seconds_attr);
      Py_DECREF(microseconds_attr);
      if (days == -1 || seconds == -1 || microseconds == -1) {
        if (PyErr_Occurred()) {
          Py_DECREF(type_name);
          return NULL;
        }
      }
      ns_val = (long long)(days * 24LL * 3600LL * 1000000000LL +
                           seconds * 1000000000LL + microseconds * 1000LL);
      Py_DECREF(type_name);
    } else {
      Py_DECREF(type_name);
      ns_val = PyLong_AsLongLong(item); // nanoseconds since epoch
      if (ns_val == -1 && PyErr_Occurred())
        return NULL;
    }
  } else {
    ns_val = PyLong_AsLongLong(item); // nanoseconds since epoch
    if (ns_val == -1 && PyErr_Occurred())
      return NULL;
  }
  return timestamp(ns_val);
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

    push_obj(&list_vec, ray_item);
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
