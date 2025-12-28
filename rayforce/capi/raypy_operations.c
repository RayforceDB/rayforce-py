#include "rayforce_c.h"

PyObject *raypy_get_obj_type(PyObject *self, PyObject *args) {
  (void)self;
  RayObject *ray_obj;

  if (!PyArg_ParseTuple(args, "O!", &RayObjectType, &ray_obj))
    return NULL;

  if (ray_obj->obj == NULL) {
    PyErr_SetString(PyExc_ValueError, "Object is NULL");
    return NULL;
  }

  return PyLong_FromLong(ray_obj->obj->type);
}
PyObject *raypy_set_obj_attrs(PyObject *self, PyObject *args) {
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
PyObject *raypy_table_keys(PyObject *self, PyObject *args) {
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
PyObject *raypy_table_values(PyObject *self, PyObject *args) {
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
PyObject *raypy_dict_keys(PyObject *self, PyObject *args) {
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
PyObject *raypy_dict_values(PyObject *self, PyObject *args) {
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
PyObject *raypy_dict_get(PyObject *self, PyObject *args) {
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
PyObject *raypy_at_idx(PyObject *self, PyObject *args) {
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
PyObject *raypy_insert_obj(PyObject *self, PyObject *args) {
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
PyObject *raypy_push_obj(PyObject *self, PyObject *args) {
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
PyObject *raypy_set_obj(PyObject *self, PyObject *args) {
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
PyObject *raypy_fill_vector(PyObject *self, PyObject *args) {
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
PyObject *raypy_fill_list(PyObject *self, PyObject *args) {
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
PyObject *raypy_get_obj_length(PyObject *self, PyObject *args) {
  (void)self;
  RayObject *ray_obj;

  if (!PyArg_ParseTuple(args, "O!", &RayObjectType, &ray_obj))
    return NULL;

  return PyLong_FromUnsignedLongLong(ray_obj->obj->len);
}
PyObject *raypy_repr_table(PyObject *self, PyObject *args) {
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
PyObject *raypy_eval_str(PyObject *self, PyObject *args) {
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
PyObject *raypy_get_error_obj(PyObject *self, PyObject *args) {
  (void)self;
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
PyObject *raypy_binary_set(PyObject *self, PyObject *args) {
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
PyObject *raypy_env_get_internal_function_by_name(PyObject *self,
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
PyObject *raypy_env_get_internal_name_by_function(PyObject *self,
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
PyObject *raypy_eval_obj(PyObject *self, PyObject *args) {
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
PyObject *raypy_quote(PyObject *self, PyObject *args) {
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
PyObject *raypy_rc(PyObject *self, PyObject *args) {
  (void)self;
  RayObject *ray_obj;

  if (!PyArg_ParseTuple(args, "O!", &RayObjectType, &ray_obj))
    return NULL;

  return PyLong_FromUnsignedLong(rc_obj(ray_obj->obj));
}
PyObject *raypy_loadfn(PyObject *self, PyObject *args) {
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
