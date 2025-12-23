#define PY_SSIZE_T_CLEAN
#include "binary.h"
#include "chrono.h"
#include "cmp.h"
#include "compose.h"
#include "cond.h"
#include "date.h"
#include "dynlib.h"
#include "env.h"
#include "error.h"
#include "eval.h"
#include "format.h"
#include "guid.h"
#include "io.h"
#include "items.h"
#include "iter.h"
#include "join.h"
#include "logic.h"
#include "math.h"
#include "misc.h"
#include "ops.h"
#include "order.h"
#include "os.h"
#include "proc.h"
#include "query.h"
#include "rayforce.h"
#include "runtime.h"
#include "serde.h"
#include "string.h"
#include "time.h"
#include "timestamp.h"
#include "unary.h"
#include "update.h"
#include "util.h"
#include "vary.h"
#include <Python.h>
#include <string.h>
#include <unistd.h>

static void *g_runtime = NULL; // where runtime is stored

#ifndef memcpy
extern void *memcpy(void *dest, const void *src, size_t n);
#endif

static PyTypeObject RayObjectType;

typedef struct {
  PyObject_HEAD obj_p obj;
} RayObject;

static void RayObject_dealloc(RayObject *self) {
  if (self->obj != NULL && self->obj != NULL_OBJ)
    drop_obj(self->obj);
  Py_TYPE(self)->tp_free((PyObject *)self);
}

// PYTHON -> RAYFORCE Conversion
// ---------------------------------------------------------------------------
static obj_p raypy_init_i16_from_py(PyObject *item) {
  long val = PyLong_AsLong(item);
  if (val == -1 && PyErr_Occurred())
    return NULL;
  return i16((i16_t)val);
}
static obj_p raypy_init_i32_from_py(PyObject *item) {
  long val = PyLong_AsLong(item);
  if (val == -1 && PyErr_Occurred())
    return NULL;
  return i32((i32_t)val);
}
static obj_p raypy_init_i64_from_py(PyObject *item) {
  long long val = PyLong_AsLongLong(item);
  if (val == -1 && PyErr_Occurred())
    return NULL;
  return i64(val);
}
static obj_p raypy_init_f64_from_py(PyObject *item) {
  double val = PyFloat_AsDouble(item);
  if (val == -1.0 && PyErr_Occurred())
    return NULL;
  return f64(val);
}
static obj_p raypy_init_c8_from_py(PyObject *item) {
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
static obj_p raypy_init_b8_from_py(PyObject *item) {
  int val = PyObject_IsTrue(item);
  if (val == -1)
    return NULL;
  return b8(val ? 1 : 0);
}
static obj_p raypy_init_symbol_from_py(PyObject *item) {
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
static obj_p raypy_init_guid_from_py(PyObject *item) {
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
static obj_p raypy_init_u8_from_py(PyObject *item) {
  long val = PyLong_AsLong(item);
  if (val == -1 && PyErr_Occurred())
    return NULL;
  return u8((unsigned char)val);
}
static obj_p raypy_init_date_from_py(PyObject *item) {
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
static obj_p raypy_init_time_from_py(PyObject *item) {
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
static obj_p raypy_init_timestamp_from_py(PyObject *item) {
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

static obj_p raypy_init_list_from_py(PyObject *item);

static obj_p raypy_init_dict_from_py(PyObject *item) {
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

static obj_p raypy_init_list_from_py(PyObject *item) {
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
// END CONVERSION HELPERS
// ---------------------------------------------------------------------------

// CONSTRUCTORS
// ---------------------------------------------------------------------------
static PyObject *raypy_init_i16(PyObject *self, PyObject *args) {
  (void)self;
  PyObject *item;
  if (!PyArg_ParseTuple(args, "O", &item))
    return NULL;

  obj_p ray_obj = raypy_init_i16_from_py(item);
  if (ray_obj == NULL) {
    Py_DECREF(item);
    return NULL;
  }

  RayObject *result = (RayObject *)RayObjectType.tp_alloc(&RayObjectType, 0);
  if (result != NULL)
    result->obj = ray_obj;

  return (PyObject *)result;
}
static PyObject *raypy_init_i32(PyObject *self, PyObject *args) {
  (void)self;
  PyObject *item;
  if (!PyArg_ParseTuple(args, "O", &item))
    return NULL;

  obj_p ray_obj = raypy_init_i32_from_py(item);
  if (ray_obj == NULL) {
    Py_DECREF(item);
    return NULL;
  }

  RayObject *result = (RayObject *)RayObjectType.tp_alloc(&RayObjectType, 0);
  if (result != NULL)
    result->obj = ray_obj;

  return (PyObject *)result;
}
static PyObject *raypy_init_i64(PyObject *self, PyObject *args) {
  (void)self;
  PyObject *item;
  if (!PyArg_ParseTuple(args, "O", &item))
    return NULL;

  obj_p ray_obj = raypy_init_i64_from_py(item);
  if (ray_obj == NULL) {
    Py_DECREF(item);
    return NULL;
  }

  RayObject *result = (RayObject *)RayObjectType.tp_alloc(&RayObjectType, 0);
  if (result != NULL)
    result->obj = ray_obj;

  return (PyObject *)result;
}
static PyObject *raypy_init_f64(PyObject *self, PyObject *args) {
  (void)self;
  PyObject *item;
  if (!PyArg_ParseTuple(args, "O", &item))
    return NULL;

  obj_p ray_obj = raypy_init_f64_from_py(item);
  if (ray_obj == NULL) {
    Py_DECREF(item);
    return NULL;
  }

  RayObject *result = (RayObject *)RayObjectType.tp_alloc(&RayObjectType, 0);
  if (result != NULL)
    result->obj = ray_obj;

  return (PyObject *)result;
}
static PyObject *raypy_init_c8(PyObject *self, PyObject *args) {
  (void)self;
  PyObject *item;
  if (!PyArg_ParseTuple(args, "O", &item))
    return NULL;

  obj_p ray_obj = raypy_init_c8_from_py(item);
  if (ray_obj == NULL) {
    return NULL;
  }

  RayObject *result = (RayObject *)RayObjectType.tp_alloc(&RayObjectType, 0);
  if (result != NULL)
    result->obj = ray_obj;

  return (PyObject *)result;
}
static PyObject *raypy_init_string(PyObject *self, PyObject *args) {
  (void)self;
  const char *value;
  Py_ssize_t len;

  if (!PyArg_ParseTuple(args, "s#", &value, &len))
    return NULL;

  RayObject *result = (RayObject *)RayObjectType.tp_alloc(&RayObjectType, 0);
  if (result != NULL) {
    result->obj = string_from_str(value, len);
    if (result->obj == NULL) {
      Py_DECREF(result);
      PyErr_SetString(PyExc_MemoryError, "Failed to create string");
      return NULL;
    }
  }

  return (PyObject *)result;
}
static PyObject *raypy_init_symbol(PyObject *self, PyObject *args) {
  (void)self;
  PyObject *item;
  if (!PyArg_ParseTuple(args, "O", &item))
    return NULL;

  obj_p ray_obj = raypy_init_symbol_from_py(item);
  if (ray_obj == NULL)
    return NULL;

  RayObject *result = (RayObject *)RayObjectType.tp_alloc(&RayObjectType, 0);
  if (result != NULL)
    result->obj = ray_obj;

  return (PyObject *)result;
}
static PyObject *raypy_init_b8(PyObject *self, PyObject *args) {
  (void)self;
  PyObject *item;
  if (!PyArg_ParseTuple(args, "O", &item))
    return NULL;

  obj_p ray_obj = raypy_init_b8_from_py(item);
  if (ray_obj == NULL) {
    Py_DECREF(item);
    return NULL;
  }

  RayObject *result = (RayObject *)RayObjectType.tp_alloc(&RayObjectType, 0);
  if (result != NULL)
    result->obj = ray_obj;

  return (PyObject *)result;
}
static PyObject *raypy_init_u8(PyObject *self, PyObject *args) {
  (void)self;
  PyObject *item;
  if (!PyArg_ParseTuple(args, "O", &item))
    return NULL;

  obj_p ray_obj = raypy_init_u8_from_py(item);
  if (ray_obj == NULL) {
    Py_DECREF(item);
    return NULL;
  }

  RayObject *result = (RayObject *)RayObjectType.tp_alloc(&RayObjectType, 0);
  if (result != NULL)
    result->obj = ray_obj;

  return (PyObject *)result;
}
static PyObject *raypy_init_date(PyObject *self, PyObject *args) {
  (void)self;
  PyObject *item;
  if (!PyArg_ParseTuple(args, "O", &item))
    return NULL;

  obj_p ray_obj = raypy_init_date_from_py(item);
  if (ray_obj == NULL) {
    return NULL;
  }

  RayObject *result = (RayObject *)RayObjectType.tp_alloc(&RayObjectType, 0);
  if (result != NULL)
    result->obj = ray_obj;

  return (PyObject *)result;
}
static PyObject *raypy_init_time(PyObject *self, PyObject *args) {
  (void)self;
  PyObject *item;
  if (!PyArg_ParseTuple(args, "O", &item))
    return NULL;

  obj_p ray_obj = raypy_init_time_from_py(item);
  if (ray_obj == NULL) {
    return NULL;
  }

  RayObject *result = (RayObject *)RayObjectType.tp_alloc(&RayObjectType, 0);
  if (result != NULL)
    result->obj = ray_obj;

  return (PyObject *)result;
}
static PyObject *raypy_init_timestamp(PyObject *self, PyObject *args) {
  (void)self;
  PyObject *item;
  if (!PyArg_ParseTuple(args, "O", &item))
    return NULL;

  obj_p ray_obj = raypy_init_timestamp_from_py(item);
  if (ray_obj == NULL) {
    return NULL;
  }

  RayObject *result = (RayObject *)RayObjectType.tp_alloc(&RayObjectType, 0);
  if (result != NULL)
    result->obj = ray_obj;

  return (PyObject *)result;
}
static PyObject *raypy_init_guid(PyObject *self, PyObject *args) {
  (void)self;
  PyObject *item;
  if (!PyArg_ParseTuple(args, "O", &item))
    return NULL;

  obj_p ray_obj = raypy_init_guid_from_py(item);
  if (ray_obj == NULL) {
    return NULL;
  }

  RayObject *result = (RayObject *)RayObjectType.tp_alloc(&RayObjectType, 0);
  if (result != NULL)
    result->obj = ray_obj;

  return (PyObject *)result;
}
static PyObject *raypy_init_list(PyObject *self, PyObject *args) {
  (void)self;
  PyObject *item = NULL;
  Py_ssize_t initial_size = 0;

  if (PyArg_ParseTuple(args, "O", &item)) {
    if (PyList_Check(item) || PyTuple_Check(item)) {
      obj_p ray_obj = raypy_init_list_from_py(item);
      if (ray_obj == NULL)
        return NULL;

      RayObject *result =
          (RayObject *)RayObjectType.tp_alloc(&RayObjectType, 0);
      if (result != NULL)
        result->obj = ray_obj;

      return (PyObject *)result;
    }
    item = NULL;
  }

  PyErr_Clear();
  if (!PyArg_ParseTuple(args, "|n", &initial_size))
    return NULL;

  RayObject *result = (RayObject *)RayObjectType.tp_alloc(&RayObjectType, 0);
  if (result != NULL) {
    result->obj = vector(TYPE_LIST, (u64_t)initial_size);
    if (result->obj == NULL) {
      Py_DECREF(result);
      PyErr_SetString(PyExc_MemoryError, "Failed to create list");
      return NULL;
    }
  }

  return (PyObject *)result;
}
static PyObject *raypy_init_table(PyObject *self, PyObject *args) {
  (void)self;
  RayObject *keys_obj;
  RayObject *vals_obj;

  if (!PyArg_ParseTuple(args, "O!O!", &RayObjectType, &keys_obj, &RayObjectType,
                        &vals_obj))
    return NULL;

  RayObject *result = (RayObject *)RayObjectType.tp_alloc(&RayObjectType, 0);
  if (result != NULL) {
    result->obj = ray_table(keys_obj->obj, vals_obj->obj);
    if (result->obj == NULL) {
      Py_DECREF(result);
      PyErr_SetString(PyExc_RuntimeError, "Failed to create table");
      return NULL;
    }
  }

  return (PyObject *)result;
}
static PyObject *raypy_init_dict(PyObject *self, PyObject *args) {
  (void)self;
  PyObject *item = NULL;
  RayObject *keys_obj;
  RayObject *vals_obj;

  if (PyArg_ParseTuple(args, "O", &item)) {
    if (PyDict_Check(item)) {
      obj_p ray_obj = raypy_init_dict_from_py(item);
      if (ray_obj == NULL)
        return NULL;

      RayObject *result =
          (RayObject *)RayObjectType.tp_alloc(&RayObjectType, 0);
      if (result != NULL)
        result->obj = ray_obj;

      return (PyObject *)result;
    }
    item = NULL;
  }

  // Try to parse as two RayObjects
  PyErr_Clear();
  if (!PyArg_ParseTuple(args, "O!O!", &RayObjectType, &keys_obj, &RayObjectType,
                        &vals_obj))
    return NULL;

  RayObject *result = (RayObject *)RayObjectType.tp_alloc(&RayObjectType, 0);
  if (result != NULL) {
    result->obj = ray_dict(keys_obj->obj, vals_obj->obj);
    if (result->obj == NULL) {
      Py_DECREF(result);
      PyErr_SetString(PyExc_RuntimeError, "Failed to create dictionary");
      return NULL;
    }
  }

  return (PyObject *)result;
}
static PyObject *raypy_init_vector(PyObject *self, PyObject *args) {
  (void)self;
  int type_code;
  Py_ssize_t length;

  if (!PyArg_ParseTuple(args, "in", &type_code, &length))
    return NULL;

  RayObject *result = (RayObject *)RayObjectType.tp_alloc(&RayObjectType, 0);
  if (result != NULL) {
    result->obj = vector(type_code, (u64_t)length);
    if (result->obj == NULL) {
      Py_DECREF(result);
      PyErr_SetString(PyExc_MemoryError, "Failed to create vector");
      return NULL;
    }
  }

  return (PyObject *)result;
}

// END CONSTRUCTORS
// ---------------------------------------------------------------------------

// READERS
// ---------------------------------------------------------------------------
static PyObject *raypy_read_i16(PyObject *self, PyObject *args) {
  (void)self;
  RayObject *ray_obj;

  if (!PyArg_ParseTuple(args, "O!", &RayObjectType, &ray_obj))
    return NULL;

  if (ray_obj->obj == NULL || ray_obj->obj->type != -TYPE_I16) {
    PyErr_SetString(PyExc_TypeError, "Object is not an i16");
    return NULL;
  }

  return PyLong_FromLong(ray_obj->obj->i16);
}
static PyObject *raypy_read_i32(PyObject *self, PyObject *args) {
  (void)self;
  RayObject *ray_obj;

  if (!PyArg_ParseTuple(args, "O!", &RayObjectType, &ray_obj))
    return NULL;

  if (ray_obj->obj == NULL || ray_obj->obj->type != -TYPE_I32) {
    PyErr_SetString(PyExc_TypeError, "Object is not an i32");
    return NULL;
  }

  return PyLong_FromLong(ray_obj->obj->i32);
}
static PyObject *raypy_read_i64(PyObject *self, PyObject *args) {
  (void)self;
  RayObject *ray_obj;

  if (!PyArg_ParseTuple(args, "O!", &RayObjectType, &ray_obj))
    return NULL;

  if (ray_obj->obj == NULL || ray_obj->obj->type != -TYPE_I64) {
    PyErr_SetString(PyExc_TypeError, "Object is not an i64");
    return NULL;
  }

  return PyLong_FromLongLong(ray_obj->obj->i64);
}
static PyObject *raypy_read_f64(PyObject *self, PyObject *args) {
  (void)self;
  RayObject *ray_obj;

  if (!PyArg_ParseTuple(args, "O!", &RayObjectType, &ray_obj))
    return NULL;

  if (ray_obj->obj == NULL || ray_obj->obj->type != -TYPE_F64) {
    PyErr_SetString(PyExc_TypeError, "Object is not an f64");
    return NULL;
  }

  return PyFloat_FromDouble(ray_obj->obj->f64);
}
static PyObject *raypy_read_c8(PyObject *self, PyObject *args) {
  (void)self;
  RayObject *ray_obj;

  if (!PyArg_ParseTuple(args, "O!", &RayObjectType, &ray_obj))
    return NULL;

  if (ray_obj->obj == NULL || ray_obj->obj->type != -TYPE_C8) {
    PyErr_SetString(PyExc_TypeError, "Object is not a c8");
    return NULL;
  }

  return PyUnicode_FromStringAndSize(&ray_obj->obj->c8, 1);
}
static PyObject *raypy_read_string(PyObject *self, PyObject *args) {
  (void)self;
  RayObject *ray_obj;
  if (!PyArg_ParseTuple(args, "O!", &RayObjectType, &ray_obj))
    return NULL;

  if (ray_obj->obj == NULL || ray_obj->obj->type != TYPE_C8) {
    PyErr_SetString(PyExc_TypeError, "Object is not a string");
    return NULL;
  }

  return PyUnicode_FromStringAndSize(AS_C8(ray_obj->obj), ray_obj->obj->len);
}
static PyObject *raypy_read_symbol(PyObject *self, PyObject *args) {
  (void)self;
  RayObject *ray_obj;

  if (!PyArg_ParseTuple(args, "O!", &RayObjectType, &ray_obj))
    return NULL;

  if (ray_obj->obj == NULL || ray_obj->obj->type != -TYPE_SYMBOL) {
    PyErr_SetString(PyExc_TypeError, "Object is not a symbol");
    return NULL;
  }

  const char *str = str_from_symbol(ray_obj->obj->i64);
  if (str == NULL)
    Py_RETURN_NONE;

  return PyUnicode_FromString(str);
}
static PyObject *raypy_read_b8(PyObject *self, PyObject *args) {
  (void)self;
  RayObject *ray_obj;

  if (!PyArg_ParseTuple(args, "O!", &RayObjectType, &ray_obj))
    return NULL;

  if (ray_obj->obj == NULL || ray_obj->obj->type != -TYPE_B8) {
    PyErr_SetString(PyExc_TypeError, "Object is not a B8 type");
    return NULL;
  }

  return PyBool_FromLong(ray_obj->obj->b8);
}
static PyObject *raypy_read_u8(PyObject *self, PyObject *args) {
  (void)self;
  RayObject *ray_obj;

  if (!PyArg_ParseTuple(args, "O!", &RayObjectType, &ray_obj))
    return NULL;

  if (ray_obj->obj == NULL || ray_obj->obj->type != -TYPE_U8) {
    PyErr_SetString(PyExc_TypeError, "Object is not a U8 type");
    return NULL;
  }

  return PyLong_FromLong((long)ray_obj->obj->u8);
}
static PyObject *raypy_read_date(PyObject *self, PyObject *args) {
  (void)self;
  RayObject *ray_obj;

  if (!PyArg_ParseTuple(args, "O!", &RayObjectType, &ray_obj))
    return NULL;

  if (ray_obj->obj == NULL || ray_obj->obj->type != -TYPE_DATE) {
    PyErr_SetString(PyExc_TypeError, "Object is not a DATE type");
    return NULL;
  }

  return PyLong_FromLong(ray_obj->obj->i32);
}
static PyObject *raypy_read_time(PyObject *self, PyObject *args) {
  (void)self;
  RayObject *ray_obj;

  if (!PyArg_ParseTuple(args, "O!", &RayObjectType, &ray_obj))
    return NULL;

  if (ray_obj->obj == NULL || ray_obj->obj->type != -TYPE_TIME) {
    PyErr_SetString(PyExc_TypeError, "Object is not a TIME type");
    return NULL;
  }

  return PyLong_FromLong(ray_obj->obj->i32);
}
static PyObject *raypy_read_timestamp(PyObject *self, PyObject *args) {
  (void)self;
  RayObject *ray_obj;

  if (!PyArg_ParseTuple(args, "O!", &RayObjectType, &ray_obj))
    return NULL;

  if (ray_obj->obj == NULL || ray_obj->obj->type != -TYPE_TIMESTAMP) {
    PyErr_SetString(PyExc_TypeError, "Object is not a TIMESTAMP type");
    return NULL;
  }

  return PyLong_FromLongLong(ray_obj->obj->i64);
}
static PyObject *raypy_read_guid(PyObject *self, PyObject *args) {
  (void)self;
  RayObject *ray_obj;

  if (!PyArg_ParseTuple(args, "O!", &RayObjectType, &ray_obj))
    return NULL;

  if (ray_obj->obj == NULL || ray_obj->obj->type != -TYPE_GUID) {
    PyErr_SetString(PyExc_TypeError, "Object is not a GUID type");
    return NULL;
  }

  return PyBytes_FromStringAndSize((const char *)AS_U8(ray_obj->obj), 16);
}
// END READERS
// ---------------------------------------------------------------------------

// TYPE INTROSPECTION
// ---------------------------------------------------------------------------
static PyObject *raypy_get_obj_type(PyObject *self, PyObject *args) {
  (void)args;
  RayObject *ray_obj = (RayObject *)self;

  if (ray_obj->obj == NULL) {
    PyErr_SetString(PyExc_ValueError, "Object is NULL");
    return NULL;
  }

  return PyLong_FromLong(ray_obj->obj->type);
}
static PyObject *raypy_set_obj_attrs(PyObject *self, PyObject *args) {
  (void)self;
  RayObject *ray_obj;
  long value;

  if (!PyArg_ParseTuple(args, "O!l", &RayObjectType, &ray_obj, &value))
    return NULL;

  if (ray_obj->obj == NULL) {
    PyErr_SetString(PyExc_ValueError, "Object is NULL");
    return NULL;
  }

  ray_obj->obj->attrs = (char)value;
  return PyLong_FromLong(ray_obj->obj->attrs);
}
// END TYPE INTROSPECTION
// ---------------------------------------------------------------------------

// TABLE OPERATIONS
// ---------------------------------------------------------------------------
static PyObject *raypy_table_keys(PyObject *self, PyObject *args) {
  (void)self;
  RayObject *ray_obj;

  if (!PyArg_ParseTuple(args, "O!", &RayObjectType, &ray_obj))
    return NULL;

  obj_p keys_list = AS_LIST(ray_obj->obj)[0];
  if (keys_list == NULL) {
    PyErr_SetString(PyExc_RuntimeError, "Table has no keys list");
    return NULL;
  }

  RayObject *result = (RayObject *)RayObjectType.tp_alloc(&RayObjectType, 0);
  if (result == NULL)
    return NULL;

  result->obj = clone_obj(keys_list);
  if (result->obj == NULL) {
    Py_DECREF(result);
    PyErr_SetString(PyExc_MemoryError, "Failed to clone keys list");
    return NULL;
  }

  return (PyObject *)result;
}
static PyObject *raypy_table_values(PyObject *self, PyObject *args) {
  (void)self;
  RayObject *ray_obj;

  if (!PyArg_ParseTuple(args, "O!", &RayObjectType, &ray_obj))
    return NULL;

  obj_p values_list = AS_LIST(ray_obj->obj)[1];
  if (values_list == NULL) {
    PyErr_SetString(PyExc_RuntimeError, "Table has no values list");
    return NULL;
  }

  RayObject *result = (RayObject *)RayObjectType.tp_alloc(&RayObjectType, 0);
  if (result == NULL)
    return NULL;

  result->obj = clone_obj(values_list);
  if (result->obj == NULL) {
    Py_DECREF(result);
    PyErr_SetString(PyExc_MemoryError, "Failed to clone values list");
    return NULL;
  }

  return (PyObject *)result;
}
// END TABLE OPERATIONS
// ---------------------------------------------------------------------------

// DICT OPERATIONS
// ---------------------------------------------------------------------------
static PyObject *raypy_dict_keys(PyObject *self, PyObject *args) {
  (void)self;
  RayObject *ray_obj;

  if (!PyArg_ParseTuple(args, "O!", &RayObjectType, &ray_obj))
    return NULL;

  obj_p keys = ray_key(ray_obj->obj);
  if (keys == NULL)
    Py_RETURN_NONE;

  RayObject *result = (RayObject *)RayObjectType.tp_alloc(&RayObjectType, 0);
  if (result == NULL)
    return NULL;

  result->obj = clone_obj(keys);
  if (result->obj == NULL) {
    Py_DECREF(result);
    PyErr_SetString(PyExc_MemoryError, "Failed to clone item");
    return NULL;
  }

  return (PyObject *)result;
}
static PyObject *raypy_dict_values(PyObject *self, PyObject *args) {
  (void)self;
  RayObject *ray_obj;

  if (!PyArg_ParseTuple(args, "O!", &RayObjectType, &ray_obj))
    return NULL;

  obj_p values = ray_value(ray_obj->obj);
  if (values == NULL)
    Py_RETURN_NONE;

  RayObject *result = (RayObject *)RayObjectType.tp_alloc(&RayObjectType, 0);
  if (result == NULL)
    return NULL;

  result->obj = clone_obj(values);
  if (result->obj == NULL) {
    Py_DECREF(result);
    PyErr_SetString(PyExc_MemoryError, "Failed to clone item");
    return NULL;
  }

  return (PyObject *)result;
}
static PyObject *raypy_dict_get(PyObject *self, PyObject *args) {
  (void)self;
  RayObject *ray_obj;
  RayObject *key_obj;

  if (!PyArg_ParseTuple(args, "O!O!", &RayObjectType, &ray_obj, &RayObjectType,
                        &key_obj))
    return NULL;

  obj_p result = at_obj(ray_obj->obj, key_obj->obj);
  if (result == NULL) {
    PyErr_SetString(PyExc_KeyError, "Key not found in dictionary");
    return NULL;
  }

  RayObject *ray_result =
      (RayObject *)RayObjectType.tp_alloc(&RayObjectType, 0);
  if (ray_result != NULL) {
    ray_result->obj = clone_obj(result);
    if (ray_result->obj == NULL) {
      Py_DECREF(ray_result);
      PyErr_SetString(PyExc_MemoryError, "Failed to clone dictionary value");
      return NULL;
    }
  }

  return (PyObject *)ray_result;
}
// END DICT OPERATIONS
// ---------------------------------------------------------------------------

// VECTOR OPERATIONS
// ---------------------------------------------------------------------------
static PyObject *raypy_at_idx(PyObject *self, PyObject *args) {
  (void)self;
  RayObject *ray_obj;
  Py_ssize_t index;

  if (!PyArg_ParseTuple(args, "O!n", &RayObjectType, &ray_obj, &index))
    return NULL;

  obj_p item = at_idx(ray_obj->obj, (i64_t)index);
  if (item == NULL)
    Py_RETURN_NONE;

  RayObject *result = (RayObject *)RayObjectType.tp_alloc(&RayObjectType, 0);
  if (result == NULL)
    return NULL;

  result->obj = clone_obj(item);
  if (result->obj == NULL) {
    Py_DECREF(result);
    PyErr_SetString(PyExc_MemoryError, "Failed to clone item");
    return NULL;
  }

  return (PyObject *)result;
}
static PyObject *raypy_insert_obj(PyObject *self, PyObject *args) {
  (void)self;
  RayObject *ray_obj;
  Py_ssize_t index;
  RayObject *item;

  if (!PyArg_ParseTuple(args, "O!nO!", &RayObjectType, &ray_obj, &index,
                        &RayObjectType, &item))
    return NULL;

  obj_p clone = clone_obj(item->obj);
  if (clone == NULL) {
    PyErr_SetString(PyExc_MemoryError, "Failed to clone item");
    return NULL;
  }

  ins_obj(&ray_obj->obj, (i64_t)index, clone);
  Py_RETURN_NONE;
}
static PyObject *raypy_push_obj(PyObject *self, PyObject *args) {
  (void)self;
  RayObject *ray_obj;
  RayObject *item;

  if (!PyArg_ParseTuple(args, "O!O!", &RayObjectType, &ray_obj, &RayObjectType,
                        &item))
    return NULL;

  obj_p clone = clone_obj(item->obj);
  if (clone == NULL) {
    PyErr_SetString(PyExc_MemoryError, "Failed to clone item");
    return NULL;
  }

  push_obj(&ray_obj->obj, clone);
  Py_RETURN_NONE;
}
static PyObject *raypy_set_obj(PyObject *self, PyObject *args) {
  (void)self;
  RayObject *ray_obj;
  RayObject *idx_obj;
  RayObject *val_obj;

  if (!PyArg_ParseTuple(args, "O!O!O!", &RayObjectType, &ray_obj,
                        &RayObjectType, &idx_obj, &RayObjectType, &val_obj))
    return NULL;

  obj_p clone = clone_obj(val_obj->obj);
  // Note: set_obj takes ownership of clone and handles all memory management:
  // - It drops clone on error
  // - It modifies ray_obj->obj through the pointer
  // - If reallocation happens (e.g., diverse_obj), it drops the old object
  // internally
  obj_p result_obj = set_obj(&ray_obj->obj, idx_obj->obj, clone);

  if (result_obj->type == TYPE_ERR) {
    PyErr_SetString(PyExc_RuntimeError, "Failed to set object");
    return NULL;
  }

  Py_RETURN_NONE;
}
static PyObject *raypy_fill_vector(PyObject *self, PyObject *args) {
  (void)self;
  RayObject *vec_obj;
  PyObject *fill;

  if (!PyArg_ParseTuple(args, "O!O", &RayObjectType, &vec_obj, &fill))
    return NULL;

  int type_code = vec_obj->obj->type;
  Py_ssize_t len = PySequence_Size(fill);
  if (len < 0)
    return NULL;

  for (Py_ssize_t i = 0; i < len; i++) {
    PyObject *item = PySequence_GetItem(fill, i);
    if (item == NULL)
      return NULL;

    obj_p ray_item = NULL;

    if (item == Py_None) {
      ray_item = NULL_OBJ;
      ins_obj(&vec_obj->obj, (i64_t)i, ray_item);
      Py_DECREF(item);
      continue;
    }

    if (PyObject_TypeCheck(item, &RayObjectType)) { // item is a RayObject
      RayObject *ray_obj = (RayObject *)item;
      if (ray_obj->obj != NULL) {
        ray_item = clone_obj(ray_obj->obj);
        if (ray_item == NULL) {
          Py_DECREF(item);
          PyErr_SetString(PyExc_MemoryError, "Failed to clone RayObject");
          return NULL;
        }
        ins_obj(&vec_obj->obj, (i64_t)i, ray_item);
        Py_DECREF(item);
        continue;
      }
    }

    if (PyObject_HasAttrString(item, "ptr")) { // item has ptr attribute
      PyObject *ptr_attr = PyObject_GetAttrString(item, "ptr");
      if (ptr_attr != NULL && PyObject_TypeCheck(ptr_attr, &RayObjectType)) {
        RayObject *ray_obj = (RayObject *)ptr_attr;
        if (ray_obj->obj != NULL) {
          ray_item = clone_obj(ray_obj->obj);
          Py_DECREF(ptr_attr);
          if (ray_item == NULL) {
            Py_DECREF(item);
            PyErr_SetString(PyExc_MemoryError,
                            "Failed to clone RayObject from ptr");
            return NULL;
          }
          ins_obj(&vec_obj->obj, (i64_t)i, ray_item);
          Py_DECREF(item);
          continue;
        }
      }
      Py_XDECREF(ptr_attr);
    }

    // I16
    if (type_code == TYPE_I16) {
      ray_item = raypy_init_i16_from_py(item);
      if (ray_item == NULL) {
        Py_DECREF(item);
        return NULL;
      }
      // I32
    } else if (type_code == TYPE_I32) {
      ray_item = raypy_init_i32_from_py(item);
      if (ray_item == NULL) {
        Py_DECREF(item);
        return NULL;
      }
      // I64
    } else if (type_code == TYPE_I64) {
      ray_item = raypy_init_i64_from_py(item);
      if (ray_item == NULL) {
        Py_DECREF(item);
        return NULL;
      }
      // F64
    } else if (type_code == TYPE_F64) {
      ray_item = raypy_init_f64_from_py(item);
      if (ray_item == NULL) {
        Py_DECREF(item);
        return NULL;
      }
      // B8
    } else if (type_code == TYPE_B8) {
      ray_item = raypy_init_b8_from_py(item);
      if (ray_item == NULL) {
        Py_DECREF(item);
        return NULL;
      }
      // SYMBOL
    } else if (type_code == TYPE_SYMBOL) {
      ray_item = raypy_init_symbol_from_py(item);
      if (ray_item == NULL) {
        Py_DECREF(item);
        return NULL;
      }
      // U8
    } else if (type_code == TYPE_U8) {
      ray_item = raypy_init_u8_from_py(item);
      if (ray_item == NULL) {
        Py_DECREF(item);
        return NULL;
      }
      // C8
    } else if (type_code == TYPE_C8) {
      ray_item = raypy_init_c8_from_py(item);
      if (ray_item == NULL) {
        Py_DECREF(item);
        return NULL;
      }
    } else if (type_code == TYPE_GUID) {
      ray_item = raypy_init_guid_from_py(item);
      if (ray_item == NULL) {
        Py_DECREF(item);
        return NULL;
      }
      // DATE
    } else if (type_code == TYPE_DATE) {
      ray_item = raypy_init_date_from_py(item);
      if (ray_item == NULL) {
        Py_DECREF(item);
        return NULL;
      }
      // TIME
    } else if (type_code == TYPE_TIME) {
      ray_item = raypy_init_time_from_py(item);
      if (ray_item == NULL) {
        Py_DECREF(item);
        return NULL;
      }
      // TIMESTAMP
    } else if (type_code == TYPE_TIMESTAMP) {
      ray_item = raypy_init_timestamp_from_py(item);
      if (ray_item == NULL) {
        Py_DECREF(item);
        return NULL;
      }
    } else {
      Py_DECREF(item);
      PyErr_SetString(PyExc_TypeError, "Unsupported type code for bulk fill");
      return NULL;
    }

    ins_obj(&vec_obj->obj, (i64_t)i, ray_item);
    Py_DECREF(item);
  }

  Py_RETURN_NONE;
}
static PyObject *raypy_fill_list(PyObject *self, PyObject *args) {
  (void)self;
  RayObject *list_obj;
  PyObject *fill;

  if (!PyArg_ParseTuple(args, "O!O", &RayObjectType, &list_obj, &fill))
    return NULL;

  if (list_obj->obj == NULL || list_obj->obj->type != TYPE_LIST) {
    PyErr_SetString(PyExc_TypeError, "Object is not a LIST type");
    return NULL;
  }

  Py_ssize_t len = PySequence_Size(fill);
  if (len < 0)
    return NULL;

  for (Py_ssize_t i = 0; i < len; i++) {
    PyObject *item = PySequence_GetItem(fill, i);
    if (item == NULL)
      return NULL;

    obj_p ray_item = NULL;

    // Check if item is None - insert NULL_OBJ
    if (item == Py_None) {
      ray_item = NULL_OBJ;
      push_obj(&list_obj->obj, ray_item);
      Py_DECREF(item);
      continue;
    }

    if (PyObject_TypeCheck(item, &RayObjectType)) { // item is a RayObject
      RayObject *ray_obj = (RayObject *)item;
      if (ray_obj->obj != NULL) {
        ray_item = clone_obj(ray_obj->obj);
        if (ray_item == NULL) {
          Py_DECREF(item);
          PyErr_SetString(PyExc_MemoryError, "Failed to clone RayObject");
          return NULL;
        }
        push_obj(&list_obj->obj, ray_item);
        Py_DECREF(item);
        continue;
      }
    }

    if (PyObject_HasAttrString(item, "ptr")) { // item has ptr attribute
      PyObject *ptr_attr = PyObject_GetAttrString(item, "ptr");
      if (ptr_attr != NULL && PyObject_TypeCheck(ptr_attr, &RayObjectType)) {
        RayObject *ray_obj = (RayObject *)ptr_attr;
        if (ray_obj->obj != NULL) {
          ray_item = clone_obj(ray_obj->obj);
          Py_DECREF(ptr_attr);
          if (ray_item == NULL) {
            Py_DECREF(item);
            PyErr_SetString(PyExc_MemoryError,
                            "Failed to clone RayObject from ptr");
            return NULL;
          }
          push_obj(&list_obj->obj, ray_item);
          Py_DECREF(item);
          continue;
        }
      }
      Py_XDECREF(ptr_attr);
    }

    if (PyBool_Check(item)) { // B8
      ray_item = raypy_init_b8_from_py(item);
    }
    // Try integer
    else if (PyLong_Check(item)) { // I64
      long val = PyLong_AsLong(item);
      if (val == -1 && PyErr_Occurred()) {
        Py_DECREF(item);
        return NULL;
      }
      ray_item = raypy_init_i64_from_py(item);
    } else if (PyFloat_Check(item)) { // F64
      ray_item = raypy_init_f64_from_py(item);
    } else if (PyUnicode_Check(item) || PyBytes_Check(item)) { // SYMBOL
      ray_item = raypy_init_symbol_from_py(item);
    } else if (PyDict_Check(item)) { // DICT
      ray_item = raypy_init_dict_from_py(item);
    } else if (PyList_Check(item) || PyTuple_Check(item)) { // LIST
      ray_item = raypy_init_list_from_py(item);
    } else {
      PyObject *type_obj = (PyObject *)Py_TYPE(item);
      PyObject *type_name = PyObject_GetAttrString(type_obj, "__name__");
      if (type_name != NULL) {
        const char *name_str = PyUnicode_AsUTF8(type_name);
        if (name_str != NULL) {
          if (strcmp(name_str, "date") == 0) { // DATE
            ray_item = raypy_init_date_from_py(item);
          } else if (strcmp(name_str, "time") == 0) { // TIME
            ray_item = raypy_init_time_from_py(item);
          } else if (strcmp(name_str, "datetime") == 0) { // TIMESTAMP
            ray_item = raypy_init_timestamp_from_py(item);
          }
        }
        Py_DECREF(type_name);
      }
    }

    if (ray_item == NULL) {
      Py_DECREF(item);
      PyErr_SetString(PyExc_TypeError, "Unsupported type for List item");
      return NULL;
    }

    push_obj(&list_obj->obj, ray_item);
    Py_DECREF(item);
  }

  Py_RETURN_NONE;
}
// END VECTOR OPERATIONS
// ---------------------------------------------------------------------------

// MISC
// ---------------------------------------------------------------------------
static PyObject *raypy_get_obj_length(PyObject *self, PyObject *args) {
  (void)self;
  RayObject *ray_obj;

  if (!PyArg_ParseTuple(args, "O!", &RayObjectType, &ray_obj))
    return NULL;

  return PyLong_FromUnsignedLongLong(ray_obj->obj->len);
}
static PyObject *raypy_repr_table(PyObject *self, PyObject *args) {
  (void)self;
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
static PyObject *raypy_eval_str(PyObject *self, PyObject *args) {
  (void)self;
  RayObject *ray_obj;

  if (!PyArg_ParseTuple(args, "O!", &RayObjectType, &ray_obj))
    return NULL;

  RayObject *result = (RayObject *)RayObjectType.tp_alloc(&RayObjectType, 0);
  if (result == NULL)
    return NULL;

  result->obj = ray_eval_str(ray_obj->obj, NULL_OBJ);
  if (result->obj == NULL) {
    Py_DECREF(result);
    PyErr_SetString(PyExc_RuntimeError, "Failed to evaluate expression");
    return NULL;
  }

  return (PyObject *)result;
}
static PyObject *raypy_get_error_message(PyObject *self, PyObject *args) {
  (void)self;
  RayObject *ray_obj;

  if (!PyArg_ParseTuple(args, "O!", &RayObjectType, &ray_obj))
    return NULL;

  ray_error_p err = AS_ERROR(ray_obj->obj);

  if (err != NULL && err->msg != NULL && err->msg->type == TYPE_C8) {
    const char *error_text = AS_C8(err->msg);
    u64_t length = err->msg->len;

    PyObject *error_message =
        PyUnicode_DecodeLatin1(error_text, length, "replace");

    if (err->locs != NULL && err->locs->type == TYPE_LIST &&
        err->locs->len > 0) {
      PyObject *with_code = PyUnicode_FromFormat(
          "%s (error code: %lld)", PyUnicode_AsUTF8(error_message),
          (long long)err->code);
      Py_DECREF(error_message);
      return with_code;
    }

    return error_message;
  }

  if (err != NULL)
    return PyUnicode_FromFormat("Error code: %lld", (long long)err->code);
  else
    return PyUnicode_FromString("Unknown error");
}
static PyObject *raypy_binary_set(PyObject *self, PyObject *args) {
  (void)self;
  RayObject *symbol_or_path;
  RayObject *value;

  if (!PyArg_ParseTuple(args, "O!O!", &RayObjectType, &symbol_or_path,
                        &RayObjectType, &value))
    return NULL;

  if (symbol_or_path->obj == NULL || value->obj == NULL) {
    PyErr_SetString(PyExc_ValueError,
                    "Neither symbol/path nor value can be NULL");
    return NULL;
  }

  if (symbol_or_path->obj->type != -TYPE_SYMBOL &&
      symbol_or_path->obj->type != TYPE_C8) {
    PyErr_SetString(PyExc_TypeError,
                    "First argument must be a symbol or string");
    return NULL;
  }

  RayObject *result = (RayObject *)RayObjectType.tp_alloc(&RayObjectType, 0);
  if (result != NULL) {
    result->obj = binary_set(symbol_or_path->obj, value->obj);
    if (result->obj == NULL) {
      Py_DECREF(result);
      PyErr_SetString(PyExc_RuntimeError, "Failed to execute set operation");
      return NULL;
    }
  }

  return (PyObject *)result;
}
static PyObject *raypy_env_get_internal_function_by_name(PyObject *self,
                                                         PyObject *args) {
  (void)self;
  const char *name;
  Py_ssize_t name_len;

  if (!PyArg_ParseTuple(args, "s#", &name, &name_len))
    return NULL;

  obj_p func_obj = env_get_internal_function(name);

  if (func_obj == NULL_OBJ || func_obj == NULL)
    Py_RETURN_NONE;

  RayObject *result = (RayObject *)RayObjectType.tp_alloc(&RayObjectType, 0);
  if (result != NULL) {
    // Clone the internal function to avoid use-after-free when Python GC
    // deallocates the RayObject. Internal functions are owned by the runtime.
    result->obj = clone_obj(func_obj);
    if (result->obj == NULL) {
      Py_DECREF(result);
      PyErr_SetString(PyExc_MemoryError, "Failed to clone internal function");
      return NULL;
    }
  }

  return (PyObject *)result;
}
static PyObject *raypy_env_get_internal_name_by_function(PyObject *self,
                                                         PyObject *args) {
  (void)self;
  RayObject *ray_obj;

  if (!PyArg_ParseTuple(args, "O!", &RayObjectType, &ray_obj))
    return NULL;

  str_p name = env_get_internal_name(ray_obj->obj);
  if (name == NULL)
    Py_RETURN_NONE;

  return PyUnicode_FromString(name);
}
static PyObject *raypy_eval_obj(PyObject *self, PyObject *args) {
  (void)self;
  RayObject *ray_obj;

  if (!PyArg_ParseTuple(args, "O!", &RayObjectType, &ray_obj))
    return NULL;

  RayObject *result = (RayObject *)RayObjectType.tp_alloc(&RayObjectType, 0);
  if (result == NULL)
    return NULL;

  result->obj = eval_obj(ray_obj->obj);
  if (result->obj == NULL) {
    Py_DECREF(result);
    PyErr_SetString(PyExc_RuntimeError, "Failed to evaluate object");
    return NULL;
  }

  return (PyObject *)result;
}
static PyObject *raypy_quote(PyObject *self, PyObject *args) {
  (void)self;
  RayObject *ray_obj;

  if (!PyArg_ParseTuple(args, "O!", &RayObjectType, &ray_obj))
    return NULL;

  RayObject *result = (RayObject *)RayObjectType.tp_alloc(&RayObjectType, 0);
  if (result == NULL)
    return NULL;

  result->obj = ray_quote(ray_obj->obj);
  if (result->obj == NULL) {
    Py_DECREF(result);
    PyErr_SetString(PyExc_RuntimeError, "Failed to quote object");
    return NULL;
  }

  return (PyObject *)result;
}
static PyObject *raypy_rc(PyObject *self, PyObject *args) {
  (void)self;
  RayObject *ray_obj;

  if (!PyArg_ParseTuple(args, "O!", &RayObjectType, &ray_obj))
    return NULL;

  return PyLong_FromUnsignedLong(rc_obj(ray_obj->obj));
}
static PyObject *raypy_loadfn(PyObject *self, PyObject *args) {
  (void)self;
  const char *path;
  const char *func_name;
  int nargs;
  Py_ssize_t path_len, func_len;

  if (!PyArg_ParseTuple(args, "s#s#i", &path, &path_len, &func_name, &func_len,
                        &nargs))
    return NULL;

  // Create raw obj_p objects without Python wrappers to avoid use-after-free
  obj_p path_obj = vector(TYPE_C8, path_len);
  if (path_obj == NULL) {
    PyErr_SetString(PyExc_MemoryError, "Failed to allocate path object");
    return NULL;
  }
  memcpy(AS_C8(path_obj), path, path_len);

  obj_p func_obj = vector(TYPE_C8, func_len);
  if (func_obj == NULL) {
    drop_obj(path_obj);
    PyErr_SetString(PyExc_MemoryError,
                    "Failed to allocate function name object");
    return NULL;
  }
  memcpy(AS_C8(func_obj), func_name, func_len);

  obj_p nargs_obj = i64((long long)nargs);
  if (nargs_obj == NULL) {
    drop_obj(path_obj);
    drop_obj(func_obj);
    PyErr_SetString(PyExc_MemoryError, "Failed to allocate nargs object");
    return NULL;
  }

  RayObject *result = (RayObject *)RayObjectType.tp_alloc(&RayObjectType, 0);
  if (result == NULL) {
    drop_obj(path_obj);
    drop_obj(func_obj);
    drop_obj(nargs_obj);
    return NULL;
  }

  obj_p args_array[3];
  args_array[0] = path_obj;
  args_array[1] = func_obj;
  args_array[2] = nargs_obj;

  result->obj = ray_loadfn(args_array, 3);

  // Clean up temporary objects - ray_loadfn clones what it needs
  drop_obj(path_obj);
  drop_obj(func_obj);
  drop_obj(nargs_obj);

  if (result->obj == NULL) {
    Py_DECREF(result);
    PyErr_SetString(PyExc_RuntimeError,
                    "Failed to load function from shared library");
    return NULL;
  }

  return (PyObject *)result;
}
// END MISC
// ---------------------------------------------------------------------------

// DATABASE OPERATIONS
// ---------------------------------------------------------------------------
static PyObject *raypy_select(PyObject *self, PyObject *args) {
  (void)self;
  RayObject *query_dict;

  if (!PyArg_ParseTuple(args, "O!", &RayObjectType, &query_dict))
    return NULL;

  RayObject *result = (RayObject *)RayObjectType.tp_alloc(&RayObjectType, 0);
  if (result == NULL)
    return NULL;

  result->obj = EVAL_WITH_CTX(ray_select(query_dict->obj), NULL_OBJ);
  if (result->obj == NULL) {
    Py_DECREF(result);
    PyErr_SetString(PyExc_RuntimeError, "Failed to execute select query");
    return NULL;
  }

  return (PyObject *)result;
}
static PyObject *raypy_update(PyObject *self, PyObject *args) {
  (void)self;
  RayObject *update_dict;

  if (!PyArg_ParseTuple(args, "O!", &RayObjectType, &update_dict))
    return NULL;

  RayObject *result = (RayObject *)RayObjectType.tp_alloc(&RayObjectType, 0);
  if (result == NULL)
    return NULL;

  result->obj = EVAL_WITH_CTX(ray_update(update_dict->obj), NULL_OBJ);
  if (result->obj == NULL) {
    Py_DECREF(result);
    PyErr_SetString(PyExc_RuntimeError, "Failed to execute update query");
    return NULL;
  }

  return (PyObject *)result;
}

static PyObject *raypy_insert(PyObject *self, PyObject *args) {
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
  result->obj = EVAL_WITH_CTX(ray_insert(ray_args, 2), NULL_OBJ);
  if (result->obj == NULL) {
    Py_DECREF(result);
    PyErr_SetString(PyExc_RuntimeError, "Failed to execute insert");
    return NULL;
  }

  return (PyObject *)result;
}

static PyObject *raypy_upsert(PyObject *self, PyObject *args) {
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
  result->obj = EVAL_WITH_CTX(ray_upsert(ray_args, 3), NULL_OBJ);
  if (result->obj == NULL) {
    Py_DECREF(result);
    PyErr_SetString(PyExc_RuntimeError, "Failed to execute upsert");
    return NULL;
  }

  return (PyObject *)result;
}
// END DATABASE OPERATIONS
// ---------------------------------------------------------------------------

// IO OPERATIONS
// ---------------------------------------------------------------------------
static PyObject *raypy_hopen(PyObject *self, PyObject *args) {
  (void)self;
  RayObject *path_obj;
  RayObject *timeout_obj = NULL;

  if (!PyArg_ParseTuple(args, "O!|O!", &RayObjectType, &path_obj,
                        &RayObjectType, &timeout_obj))
    return NULL;

  obj_p ray_args[2];
  i64_t arg_count = 1;
  ray_args[0] = path_obj->obj;

  if (timeout_obj != NULL) {
    ray_args[1] = timeout_obj->obj;
    arg_count = 2;
  }

  RayObject *result = (RayObject *)RayObjectType.tp_alloc(&RayObjectType, 0);
  if (result == NULL)
    return NULL;

  result->obj = ray_hopen(ray_args, arg_count);
  if (result->obj == NULL) {
    Py_DECREF(result);
    PyErr_SetString(PyExc_RuntimeError, "Failed to open handle");
    return NULL;
  }

  return (PyObject *)result;
}

static PyObject *raypy_hclose(PyObject *self, PyObject *args) {
  (void)self;
  RayObject *handle_obj;

  if (!PyArg_ParseTuple(args, "O!", &RayObjectType, &handle_obj))
    return NULL;

  RayObject *result = (RayObject *)RayObjectType.tp_alloc(&RayObjectType, 0);
  if (result == NULL)
    return NULL;

  result->obj = ray_hclose(handle_obj->obj);
  if (result->obj == NULL) {
    Py_DECREF(result);
    PyErr_SetString(PyExc_RuntimeError, "Failed to close handle");
    return NULL;
  }

  return (PyObject *)result;
}

static PyObject *raypy_write(PyObject *self, PyObject *args) {
  (void)self;
  RayObject *handle_obj;
  RayObject *data_obj;

  if (!PyArg_ParseTuple(args, "O!O!", &RayObjectType, &handle_obj,
                        &RayObjectType, &data_obj))
    return NULL;

  RayObject *result = (RayObject *)RayObjectType.tp_alloc(&RayObjectType, 0);
  if (result == NULL)
    return NULL;

  result->obj = ray_write(handle_obj->obj, data_obj->obj);
  if (result->obj == NULL) {
    Py_DECREF(result);
    PyErr_SetString(PyExc_RuntimeError, "Failed to write data");
    return NULL;
  }

  return (PyObject *)result;
}
// END IO OPERATIONS
// ---------------------------------------------------------------------------

static PyMethodDef RayObject_methods[] = {
    {"get_obj_type", raypy_get_obj_type, METH_VARARGS, "Get object type"},
    {NULL, NULL, 0, NULL}};

static PyTypeObject RayObjectType = {
    PyVarObject_HEAD_INIT(NULL, 0).tp_name = "_rayforce_c.RayObject",
    .tp_basicsize = sizeof(RayObject),
    .tp_itemsize = 0,
    .tp_dealloc = (destructor)RayObject_dealloc,
    .tp_flags = Py_TPFLAGS_DEFAULT,
    .tp_doc = "RayObject objects",
    .tp_methods = RayObject_methods,
    .tp_new = PyType_GenericNew,
};

static PyMethodDef module_methods[] = {
    // Constructors
    {"init_i16", raypy_init_i16, METH_VARARGS, "Create a new i16 object"},
    {"init_i32", raypy_init_i32, METH_VARARGS, "Create a new i32 object"},
    {"init_i64", raypy_init_i64, METH_VARARGS, "Create a new i64 object"},
    {"init_f64", raypy_init_f64, METH_VARARGS, "Create a new f64 object"},
    {"init_c8", raypy_init_c8, METH_VARARGS,
     "Create a new c8 (character) object"},
    {"init_string", raypy_init_string, METH_VARARGS,
     "Create a new string object"},
    {"init_symbol", raypy_init_symbol, METH_VARARGS,
     "Create a new symbol object"},
    {"init_b8", raypy_init_b8, METH_VARARGS,
     "Create a new b8 (boolean) object"},
    {"init_u8", raypy_init_u8, METH_VARARGS, "Create a new u8 (byte) object"},
    {"init_date", raypy_init_date, METH_VARARGS, "Create a new date object"},
    {"init_time", raypy_init_time, METH_VARARGS, "Create a new time object"},
    {"init_timestamp", raypy_init_timestamp, METH_VARARGS,
     "Create a new timestamp object"},
    {"init_guid", raypy_init_guid, METH_VARARGS, "Create a new GUID object"},
    {"init_list", raypy_init_list, METH_VARARGS, "Create a new list object"},
    {"init_table", raypy_init_table, METH_VARARGS, "Create a new table object"},
    {"init_dict", raypy_init_dict, METH_VARARGS,
     "Create a new dictionary object"},
    {"init_vector", raypy_init_vector, METH_VARARGS,
     "Create a new vector object"},

    // Readers
    {"read_i16", raypy_read_i16, METH_VARARGS, "Read i16 value from object"},
    {"read_i32", raypy_read_i32, METH_VARARGS, "Read i32 value from object"},
    {"read_i64", raypy_read_i64, METH_VARARGS, "Read i64 value from object"},
    {"read_f64", raypy_read_f64, METH_VARARGS, "Read f64 value from object"},
    {"read_c8", raypy_read_c8, METH_VARARGS, "Read c8 value from object"},
    {"read_string", raypy_read_string, METH_VARARGS,
     "Read string value from object"},
    {"read_symbol", raypy_read_symbol, METH_VARARGS,
     "Read symbol value from object"},
    {"read_b8", raypy_read_b8, METH_VARARGS, "Read b8 value from object"},
    {"read_u8", raypy_read_u8, METH_VARARGS, "Read u8 value from object"},
    {"read_date", raypy_read_date, METH_VARARGS, "Read date value from object"},
    {"read_time", raypy_read_time, METH_VARARGS, "Read time value from object"},
    {"read_timestamp", raypy_read_timestamp, METH_VARARGS,
     "Read timestamp value from object"},
    {"read_guid", raypy_read_guid, METH_VARARGS, "Read GUID value from object"},

    // Table operations
    {"table_keys", raypy_table_keys, METH_VARARGS, "Get table keys"},
    {"table_values", raypy_table_values, METH_VARARGS, "Get table values"},
    {"repr_table", raypy_repr_table, METH_VARARGS, "Format table"},

    // Dictionary operations
    {"dict_keys", raypy_dict_keys, METH_VARARGS, "Get dictionary keys"},
    {"dict_values", raypy_dict_values, METH_VARARGS, "Get dictionary values"},
    {"dict_get", raypy_dict_get, METH_VARARGS, "Get value from dictionary"},

    // Vector operations
    {"at_idx", raypy_at_idx, METH_VARARGS, "Get element at index"},
    {"insert_obj", raypy_insert_obj, METH_VARARGS, "Insert object at index"},
    {"push_obj", raypy_push_obj, METH_VARARGS,
     "Push object to the end of iterable"},
    {"set_obj", raypy_set_obj, METH_VARARGS, "Set object at index"},
    {"fill_vector", raypy_fill_vector, METH_VARARGS,
     "Fill vector from Python list (bulk operation)"},
    {"fill_list", raypy_fill_list, METH_VARARGS,
     "Fill list from Python list (bulk operation)"},

    // Misc operations
    {"get_obj_length", raypy_get_obj_length, METH_VARARGS, "Get object length"},
    {"eval_str", raypy_eval_str, METH_VARARGS, "Evaluate string expression"},
    {"get_error_message", raypy_get_error_message, METH_VARARGS,
     "Get error message"},
    {"binary_set", raypy_binary_set, METH_VARARGS,
     "Set value to symbol or file"},
    {"env_get_internal_function_by_name",
     raypy_env_get_internal_function_by_name, METH_VARARGS,
     "Get internal function by name"},
    {"env_get_internal_name_by_function",
     raypy_env_get_internal_name_by_function, METH_VARARGS,
     "Get internal function name"},
    {"eval_obj", raypy_eval_obj, METH_VARARGS, "Evaluate object"},
    {"eval_obj", raypy_eval_obj, METH_VARARGS, "Evaluate a RayObject"},
    {"loadfn_from_file", raypy_loadfn, METH_VARARGS,
     "Load function from shared library"},
    {"quote", raypy_quote, METH_VARARGS, "Quote (clone) object"},
    {"rc_obj", raypy_rc, METH_VARARGS, "Get reference count of object"},
    {"set_obj_attrs", raypy_set_obj_attrs, METH_VARARGS,
     "Set object attributes"},

    // Database operations
    {"select", raypy_select, METH_VARARGS, "Perform SELECT query"},
    {"update", raypy_update, METH_VARARGS, "Perform UPDATE query"},
    {"insert", raypy_insert, METH_VARARGS, "Perform INSERT query"},
    {"upsert", raypy_upsert, METH_VARARGS, "Perform UPSERT query"},

    // IO operations
    {"hopen", raypy_hopen, METH_VARARGS, "Open file or socket handle"},
    {"hclose", raypy_hclose, METH_VARARGS, "Close file or socket handle"},
    {"write", raypy_write, METH_VARARGS, "Write data to file or socket"},

    {NULL, NULL, 0, NULL}};

static struct PyModuleDef rayforce_module = {
    PyModuleDef_HEAD_INIT,
    .m_name = "_rayforce_c",
    .m_doc = "Python C API bus to Rayforce",
    .m_size = -1,
    .m_methods = module_methods,
};

static RayObject *g_null_obj = NULL;

PyMODINIT_FUNC PyInit__rayforce_c(void) {
  PyObject *m;

  if (PyType_Ready(&RayObjectType) < 0)
    return NULL;

  m = PyModule_Create(&rayforce_module);
  if (m == NULL)
    return NULL;

  Py_INCREF(&RayObjectType);

  // Make RayObjectType accessible from .RayObject
  if (PyModule_AddObject(m, "RayObject", (PyObject *)&RayObjectType) < 0) {
    Py_DECREF(&RayObjectType);
    Py_DECREF(m);
    return NULL;
  }

  PyModule_AddIntConstant(m, "TYPE_LIST", TYPE_LIST);
  PyModule_AddIntConstant(m, "TYPE_B8", TYPE_B8);
  PyModule_AddIntConstant(m, "TYPE_U8", TYPE_U8);
  PyModule_AddIntConstant(m, "TYPE_I16", TYPE_I16);
  PyModule_AddIntConstant(m, "TYPE_I32", TYPE_I32);
  PyModule_AddIntConstant(m, "TYPE_I64", TYPE_I64);
  PyModule_AddIntConstant(m, "TYPE_SYMBOL", TYPE_SYMBOL);
  PyModule_AddIntConstant(m, "TYPE_DATE", TYPE_DATE);
  PyModule_AddIntConstant(m, "TYPE_TIME", TYPE_TIME);
  PyModule_AddIntConstant(m, "TYPE_TIMESTAMP", TYPE_TIMESTAMP);
  PyModule_AddIntConstant(m, "TYPE_F64", TYPE_F64);
  PyModule_AddIntConstant(m, "TYPE_GUID", TYPE_GUID);
  PyModule_AddIntConstant(m, "TYPE_C8", TYPE_C8);
  PyModule_AddIntConstant(m, "TYPE_ENUM", TYPE_ENUM);
  PyModule_AddIntConstant(m, "TYPE_MAPFILTER", TYPE_MAPFILTER);
  PyModule_AddIntConstant(m, "TYPE_MAPGROUP", TYPE_MAPGROUP);
  PyModule_AddIntConstant(m, "TYPE_MAPFD", TYPE_MAPFD);
  PyModule_AddIntConstant(m, "TYPE_MAPCOMMON", TYPE_MAPCOMMON);
  PyModule_AddIntConstant(m, "TYPE_MAPLIST", TYPE_MAPLIST);
  PyModule_AddIntConstant(m, "TYPE_PARTEDLIST", TYPE_PARTEDLIST);
  PyModule_AddIntConstant(m, "TYPE_TABLE", TYPE_TABLE);
  PyModule_AddIntConstant(m, "TYPE_DICT", TYPE_DICT);
  PyModule_AddIntConstant(m, "TYPE_LAMBDA", TYPE_LAMBDA);
  PyModule_AddIntConstant(m, "TYPE_UNARY", TYPE_UNARY);
  PyModule_AddIntConstant(m, "TYPE_BINARY", TYPE_BINARY);
  PyModule_AddIntConstant(m, "TYPE_VARY", TYPE_VARY);
  PyModule_AddIntConstant(m, "TYPE_TOKEN", TYPE_TOKEN);
  PyModule_AddIntConstant(m, "TYPE_NULL", TYPE_NULL);
  PyModule_AddIntConstant(m, "TYPE_ERR", TYPE_ERR);

  g_null_obj = (RayObject *)RayObjectType.tp_alloc(&RayObjectType, 0);
  if (g_null_obj == NULL) {
    Py_DECREF(m);
    return NULL;
  }

  g_null_obj->obj = NULL_OBJ;
  Py_INCREF(g_null_obj);

  if (PyModule_AddObject(m, "NULL_OBJ", (PyObject *)g_null_obj) < 0) {
    Py_DECREF(g_null_obj);
    Py_DECREF(m);
    return NULL;
  }

  char *argv[] = {"raypy", "-r", "0", NULL};
  g_runtime = runtime_create(3, argv);
  if (g_runtime == NULL) {
    PyErr_SetString(PyExc_RuntimeError, "Failed to initialize Rayforce");
    return NULL;
  }

  return m;
}
