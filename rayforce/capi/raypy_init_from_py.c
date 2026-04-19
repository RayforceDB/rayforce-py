#include "rayforce_c.h"
#include <ctype.h>
#include <stdio.h>
#include <stdlib.h>
#include <time.h>

#ifdef __APPLE__
#include <mach/mach_time.h>
#endif

PyObject *raypy_init_i16(PyObject *self, PyObject *args) {
  (void)self;
  CHECK_MAIN_THREAD();

  PyObject *item;
  if (!PyArg_ParseTuple(args, "O", &item))
    return NULL;

  obj_p ray_obj = raypy_init_i16_from_py(item);
  if (ray_obj == NULL) {
    PyErr_SetString(PyExc_RuntimeError,
                    "init: failed to create i16 from Python object");
    return NULL;
  }
  return raypy_wrap_ray_object(ray_obj);
}
PyObject *raypy_init_i32(PyObject *self, PyObject *args) {
  (void)self;
  CHECK_MAIN_THREAD();

  PyObject *item;
  if (!PyArg_ParseTuple(args, "O", &item))
    return NULL;

  obj_p ray_obj = raypy_init_i32_from_py(item);
  if (ray_obj == NULL) {
    PyErr_SetString(PyExc_RuntimeError,
                    "init: failed to create i32 from Python object");
    return NULL;
  }
  return raypy_wrap_ray_object(ray_obj);
}
PyObject *raypy_init_i64(PyObject *self, PyObject *args) {
  (void)self;
  CHECK_MAIN_THREAD();

  PyObject *item;
  if (!PyArg_ParseTuple(args, "O", &item))
    return NULL;

  obj_p ray_obj = raypy_init_i64_from_py(item);
  if (ray_obj == NULL) {
    PyErr_SetString(PyExc_RuntimeError,
                    "init: failed to create i64 from Python object");
    return NULL;
  }
  return raypy_wrap_ray_object(ray_obj);
}
PyObject *raypy_init_f64(PyObject *self, PyObject *args) {
  (void)self;
  CHECK_MAIN_THREAD();

  PyObject *item;
  if (!PyArg_ParseTuple(args, "O", &item))
    return NULL;

  obj_p ray_obj = raypy_init_f64_from_py(item);
  if (ray_obj == NULL) {
    PyErr_SetString(PyExc_RuntimeError,
                    "init: failed to create f64 from Python object");
    return NULL;
  }
  return raypy_wrap_ray_object(ray_obj);
}
PyObject *raypy_init_c8(PyObject *self, PyObject *args) {
  (void)self;
  CHECK_MAIN_THREAD();

  PyObject *item;
  if (!PyArg_ParseTuple(args, "O", &item))
    return NULL;

  obj_p ray_obj = raypy_init_c8_from_py(item);
  if (ray_obj == NULL) {
    PyErr_SetString(PyExc_RuntimeError,
                    "init: failed to create c8 from Python object");
    return NULL;
  }
  return raypy_wrap_ray_object(ray_obj);
}
PyObject *raypy_init_string(PyObject *self, PyObject *args) {
  (void)self;
  CHECK_MAIN_THREAD();

  PyObject *item;
  if (!PyArg_ParseTuple(args, "O", &item))
    return NULL;

  obj_p ray_obj = raypy_init_string_from_py(item);
  if (ray_obj == NULL) {
    PyErr_SetString(PyExc_RuntimeError,
                    "init: failed to create string from Python object");
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

  obj_p ray_obj = raypy_init_symbol_from_py(item);
  if (ray_obj == NULL) {
    PyErr_SetString(PyExc_RuntimeError,
                    "init: failed to create symbol from Python object");
    return NULL;
  }
  return raypy_wrap_ray_object(ray_obj);
}
PyObject *raypy_init_b8(PyObject *self, PyObject *args) {
  (void)self;
  CHECK_MAIN_THREAD();

  PyObject *item;
  if (!PyArg_ParseTuple(args, "O", &item))
    return NULL;

  obj_p ray_obj = raypy_init_b8_from_py(item);
  if (ray_obj == NULL) {
    PyErr_SetString(PyExc_RuntimeError,
                    "init: failed to create b8 from Python object");
    return NULL;
  }
  return raypy_wrap_ray_object(ray_obj);
}
PyObject *raypy_init_u8(PyObject *self, PyObject *args) {
  (void)self;
  CHECK_MAIN_THREAD();

  PyObject *item;
  if (!PyArg_ParseTuple(args, "O", &item))
    return NULL;

  obj_p ray_obj = raypy_init_u8_from_py(item);
  if (ray_obj == NULL) {
    PyErr_SetString(PyExc_RuntimeError,
                    "init: failed to create u8 from Python object");
    return NULL;
  }
  return raypy_wrap_ray_object(ray_obj);
}
PyObject *raypy_init_date(PyObject *self, PyObject *args) {
  (void)self;
  CHECK_MAIN_THREAD();

  PyObject *item;
  if (!PyArg_ParseTuple(args, "O", &item))
    return NULL;

  obj_p ray_obj = raypy_init_date_from_py(item);
  if (ray_obj == NULL) {
    PyErr_SetString(PyExc_RuntimeError,
                    "init: failed to create date from Python object");
    return NULL;
  }
  return raypy_wrap_ray_object(ray_obj);
}
PyObject *raypy_init_time(PyObject *self, PyObject *args) {
  (void)self;
  CHECK_MAIN_THREAD();

  PyObject *item;
  if (!PyArg_ParseTuple(args, "O", &item))
    return NULL;

  obj_p ray_obj = raypy_init_time_from_py(item);
  if (ray_obj == NULL) {
    PyErr_SetString(PyExc_RuntimeError,
                    "init: failed to create time from Python object");
    return NULL;
  }
  return raypy_wrap_ray_object(ray_obj);
}
PyObject *raypy_init_timestamp(PyObject *self, PyObject *args) {
  (void)self;
  CHECK_MAIN_THREAD();

  PyObject *item;
  if (!PyArg_ParseTuple(args, "O", &item))
    return NULL;

  obj_p ray_obj = raypy_init_timestamp_from_py(item);
  if (ray_obj == NULL) {
    PyErr_SetString(PyExc_RuntimeError,
                    "init: failed to create timestamp from Python object");
    return NULL;
  }
  return raypy_wrap_ray_object(ray_obj);
}
PyObject *raypy_init_guid(PyObject *self, PyObject *args) {
  (void)self;
  CHECK_MAIN_THREAD();

  PyObject *item;
  if (!PyArg_ParseTuple(args, "O", &item))
    return NULL;

  obj_p ray_obj = raypy_init_guid_from_py(item);
  if (ray_obj == NULL) {
    PyErr_SetString(PyExc_RuntimeError,
                    "init: failed to create guid from Python object");
    return NULL;
  }
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
    PyErr_SetString(PyExc_RuntimeError,
                    "init: failed to create list from Python object");
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

  obj_p keys = keys_obj->obj;
  obj_p vals = vals_obj->obj;
  if (keys == NULL || vals == NULL) {
    PyErr_SetString(PyExc_RuntimeError,
                    "init: table requires non-null keys and values");
    return NULL;
  }

  /* v2 ray_table requires names as a list of sym atoms. High-level Python code
   * passes a symbol vector. Accept either form; use ray_table_new + add_col
   * directly so we don't depend on ray_table's unbox path. */
  int64_t ncols;
  int keys_is_sym_vec = (keys->type == RAY_SYM);
  int keys_is_list = (keys->type == RAY_LIST);
  if (keys_is_sym_vec || keys_is_list) {
    ncols = keys->len;
  } else {
    PyErr_SetString(PyExc_RuntimeError,
                    "init: table keys must be a symbol vector or list");
    return NULL;
  }
  if (vals->type != RAY_LIST) {
    PyErr_SetString(PyExc_RuntimeError, "init: table values must be a list");
    return NULL;
  }
  if (vals->len != ncols) {
    /* Return a ray_t ERROR so the Python error_handler wrapper can map
     * code "length" → RayforceLengthError. */
    return raypy_wrap_ray_object(ray_error("length", NULL));
  }

  obj_p tbl = ray_table_new(ncols);
  if (tbl == NULL || RAY_IS_ERR(tbl)) {
    if (tbl)
      ray_release(tbl);
    PyErr_SetString(PyExc_RuntimeError, "init: failed to create table");
    return NULL;
  }

  ray_t **col_elems = (ray_t **)ray_data(vals);

  for (int64_t i = 0; i < ncols; i++) {
    int64_t name_id;
    if (keys_is_sym_vec) {
      int64_t *ids = (int64_t *)ray_data(keys);
      name_id = ids[i];
    } else {
      ray_t **key_elems = (ray_t **)ray_data(keys);
      if (key_elems[i] == NULL || key_elems[i]->type != -RAY_SYM) {
        ray_release(tbl);
        PyErr_SetString(PyExc_RuntimeError,
                        "init: table key elements must be symbols");
        return NULL;
      }
      name_id = key_elems[i]->i64;
    }

    obj_p col = col_elems[i];
    if (col == NULL) {
      ray_release(tbl);
      PyErr_SetString(PyExc_RuntimeError, "init: table column is null");
      return NULL;
    }
    /* ray_table_add_col retains col internally; caller keeps ownership via
     * `vals`, so no explicit retain/release is needed here. */
    obj_p res = ray_table_add_col(tbl, name_id, col);
    if (res == NULL || RAY_IS_ERR(res)) {
      ray_release(tbl);
      PyErr_Format(PyExc_RuntimeError,
                   "init: failed to add column %lld to table", (long long)i);
      return NULL;
    }
    /* ray_table_add_col may return a new pointer (realloc). */
    tbl = res;
  }

  return raypy_wrap_ray_object(tbl);
}
PyObject *raypy_init_dict(PyObject *self, PyObject *args) {
  (void)self;
  CHECK_MAIN_THREAD();

  RayObject *keys_obj;
  RayObject *vals_obj;

  if (!PyArg_ParseTuple(args, "O!O!", &RayObjectType, &keys_obj, &RayObjectType,
                        &vals_obj))
    return NULL;

  obj_p keys = keys_obj->obj;
  obj_p vals = vals_obj->obj;
  if (keys == NULL || vals == NULL) {
    PyErr_SetString(PyExc_RuntimeError,
                    "init: dict requires non-null keys and values");
    return NULL;
  }

  /* Length check so Python-level error_handler can map to RayforceLengthError.
   */
  if (keys->len != vals->len) {
    return raypy_wrap_ray_object(ray_error("length", NULL));
  }

  obj_p ray_obj = ray_dict_fn(keys, vals);
  if (ray_obj == NULL) {
    PyErr_SetString(PyExc_RuntimeError, "init: failed to create dictionary");
    return NULL;
  }
  return raypy_wrap_ray_object(ray_obj);
}

static obj_p convert_py_item_to_ray(PyObject *item, int type_code);

/* Append a converted ray atom to the target collection.
 * For RAY_LIST / RAY_STR vectors / typed scalar vectors we choose the
 * appropriate v2 append function and reassign the target pointer (which
 * may have moved after a realloc). Returns 0 on success, -1 on error.
 *
 * When `atom` is the NULL_OBJ singleton we append a zero placeholder and
 * then set the v2 null bitmap bit for the new index, so downstream readers
 * that consult `ray_vec_is_null` can tell null from zero. */
static int append_to_collection(obj_p *target_obj, obj_p atom) {
  obj_p target = *target_obj;
  if (target == NULL || atom == NULL)
    return -1;

  bool is_null = RAY_IS_NULL(atom);

  if (target->type == RAY_LIST) {
    obj_p result = ray_list_append(target, atom);
    if (result == NULL || RAY_IS_ERR(result))
      return -1;
    *target_obj = result;
    return 0;
  }

  if (target->type == RAY_STR) {
    obj_p result;
    if (is_null) {
      result = ray_str_vec_append(target, "", 0);
    } else {
      if (atom->type != -RAY_STR)
        return -1;
      result = ray_str_vec_append(target, ray_str_ptr(atom), ray_str_len(atom));
    }
    if (result == NULL || RAY_IS_ERR(result))
      return -1;
    if (is_null)
      ray_vec_set_null(result, result->len - 1, true);
    *target_obj = result;
    return 0;
  }

  /* Typed scalar vec — extract the raw scalar from the atom. */
  union {
    uint8_t u8;
    int16_t i16;
    int32_t i32;
    int64_t i64;
    double f64;
  } scratch;
  const void *p;
  if (is_null) {
    memset(&scratch, 0, sizeof(scratch));
    p = &scratch;
    if (target->type == RAY_GUID) {
      static const uint8_t zero_guid[16] = {0};
      obj_p result = ray_vec_append(target, zero_guid);
      if (result == NULL || RAY_IS_ERR(result))
        return -1;
      ray_vec_set_null(result, result->len - 1, true);
      *target_obj = result;
      return 0;
    }
  } else {
    switch (target->type) {
    case RAY_BOOL:
    case RAY_U8:
      scratch.u8 = atom->u8;
      p = &scratch.u8;
      break;
    case RAY_I16:
      scratch.i16 = atom->i16;
      p = &scratch.i16;
      break;
    case RAY_I32:
    case RAY_DATE:
    case RAY_TIME:
      scratch.i32 = atom->i32;
      p = &scratch.i32;
      break;
    case RAY_I64:
    case RAY_TIMESTAMP:
    case RAY_SYM:
      scratch.i64 = atom->i64;
      p = &scratch.i64;
      break;
    case RAY_F64:
      scratch.f64 = atom->f64;
      p = &scratch.f64;
      break;
    case RAY_GUID: {
      obj_p result =
          ray_vec_append(target, atom->obj ? ray_data(atom->obj) : NULL);
      if (result == NULL || RAY_IS_ERR(result))
        return -1;
      *target_obj = result;
      return 0;
    }
    default:
      return -1;
    }
  }
  obj_p result = ray_vec_append(target, p);
  if (result == NULL || RAY_IS_ERR(result))
    return -1;
  if (is_null)
    ray_vec_set_null(result, result->len - 1, true);
  *target_obj = result;
  return 0;
}

static int fill_obj_from_py_sequence(obj_p *target_obj, PyObject *fill,
                                     int type_code, const char *error_msg) {
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
      PyErr_SetString(PyExc_RuntimeError, error_msg);
      return -1;
    }

    if (append_to_collection(target_obj, ray_item) < 0) {
      ray_release(ray_item);
      PyErr_SetString(PyExc_RuntimeError,
                      "init: failed to append item to collection");
      return -1;
    }
    /* append_to_collection retains internally; release our reference. */
    ray_release(ray_item);
  }

  return 0;
}

/* Helper: element size (bytes) for typed vec types — used to zero-init
 * pre-sized vectors. Returns 0 for unsupported types. */
static size_t vec_elem_size_for_init(int8_t type) {
  switch (type) {
  case RAY_BOOL:
  case RAY_U8:
    return 1;
  case RAY_I16:
    return 2;
  case RAY_I32:
  case RAY_DATE:
  case RAY_TIME:
  case RAY_F32:
    return 4;
  case RAY_I64:
  case RAY_F64:
  case RAY_TIMESTAMP:
  case RAY_SYM:
    return 8;
  case RAY_GUID:
    return 16;
  case RAY_STR:
    return 16; /* ray_str_t footprint */
  default:
    return 0;
  }
}

PyObject *raypy_init_vector(PyObject *self, PyObject *args) {
  (void)self;
  CHECK_MAIN_THREAD();

  int type_code;
  PyObject *second_arg;
  if (!PyArg_ParseTuple(args, "iO", &type_code, &second_arg))
    return NULL;

  obj_p ray_obj = NULL;
  int vector_type_code = type_code < 0 ? -type_code : type_code;

  /* RAY_NULL isn't a real vec element type — fall back to RAY_LIST. */
  if (vector_type_code == RAY_NULL)
    vector_type_code = RAY_LIST;

  if (PyLong_Check(second_arg)) {
    Py_ssize_t length = PyLong_AsSsize_t(second_arg);
    if (length < 0 && PyErr_Occurred())
      return NULL;

    if (vector_type_code == RAY_LIST) {
      ray_obj = ray_list_new((int64_t)length);
      /* Fill with NULL atoms so the list has actual elements, not just cap. */
      if (ray_obj != NULL && !RAY_IS_ERR(ray_obj) && length > 0) {
        for (Py_ssize_t i = 0; i < length; i++) {
          ray_obj = ray_list_append(ray_obj, RAY_NULL_OBJ);
          if (ray_obj == NULL || RAY_IS_ERR(ray_obj))
            break;
        }
      }
    } else {
      ray_obj = ray_vec_new((int8_t)vector_type_code, (int64_t)length);
      if (ray_obj != NULL && !RAY_IS_ERR(ray_obj) && length > 0) {
        size_t esz = vec_elem_size_for_init((int8_t)vector_type_code);
        if (esz > 0) {
          memset(ray_data(ray_obj), 0, (size_t)length * esz);
        }
        ray_obj->len = (int64_t)length;
      }
    }
    if (ray_obj == NULL || RAY_IS_ERR(ray_obj)) {
      PyErr_SetString(PyExc_RuntimeError, "init: failed to create vector");
      if (ray_obj)
        ray_release(ray_obj);
      return NULL;
    }
  } else if (PySequence_Check(second_arg)) {
    Py_ssize_t len = PySequence_Size(second_arg);
    if (len < 0)
      return NULL;

    if (vector_type_code == RAY_LIST) {
      ray_obj = ray_list_new(0);
    } else {
      ray_obj = ray_vec_new((int8_t)vector_type_code, (int64_t)len);
    }
    if (ray_obj == NULL || RAY_IS_ERR(ray_obj)) {
      PyErr_SetString(PyExc_RuntimeError, "init: failed to create vector");
      if (ray_obj)
        ray_release(ray_obj);
      return NULL;
    }

    if (fill_obj_from_py_sequence(&ray_obj, second_arg, vector_type_code,
                                  "init: unsupported type code for bulk fill") <
        0) {
      ray_release(ray_obj);
      return NULL;
    }
  } else {
    PyErr_SetString(PyExc_RuntimeError,
                    "init: second argument must be an integer (length) or a "
                    "sequence (items)");
    return NULL;
  }

  return raypy_wrap_ray_object(ray_obj);
}

// CONVERSION UTILS
obj_p raypy_init_i16_from_py(PyObject *item) {
  long val = PyLong_AsLong(item);
  if (val == -1 && PyErr_Occurred())
    return NULL;
  return ray_i16((int16_t)val);
}
obj_p raypy_init_i32_from_py(PyObject *item) {
  long val = PyLong_AsLong(item);
  if (val == -1 && PyErr_Occurred())
    return NULL;
  return ray_i32((int32_t)val);
}
obj_p raypy_init_i64_from_py(PyObject *item) {
  long long val = PyLong_AsLongLong(item);
  if (val == -1 && PyErr_Occurred())
    return NULL;
  return ray_i64(val);
}
obj_p raypy_init_f64_from_py(PyObject *item) {
  double val = PyFloat_AsDouble(item);
  if (val == -1.0 && PyErr_Occurred())
    return NULL;
  return ray_f64(val);
}
obj_p raypy_init_c8_from_py(PyObject *item) {
  Py_ssize_t str_len;
  const char *str_val = PyUnicode_AsUTF8AndSize(item, &str_len);
  if (str_val == NULL)
    return NULL;
  char ch = str_len > 0 ? str_val[0] : '\0';
  return ray_str(&ch, 1);
}
obj_p raypy_init_string_from_py(PyObject *item) {
  Py_ssize_t str_len;
  const char *str_val = PyUnicode_AsUTF8AndSize(item, &str_len);
  if (str_val == NULL)
    return NULL;
  return ray_str(str_val, (size_t)str_len);
}
obj_p raypy_init_b8_from_py(PyObject *item) {
  int val = PyObject_IsTrue(item);
  if (val == -1)
    return NULL;
  return ray_bool(val ? true : false);
}
obj_p raypy_init_u8_from_py(PyObject *item) {
  long val = PyLong_AsLong(item);
  if (val == -1 && PyErr_Occurred())
    return NULL;
  return ray_u8((uint8_t)val);
}
obj_p raypy_init_symbol_from_py(PyObject *item) {
  Py_ssize_t str_len;
  const char *str_val = PyUnicode_AsUTF8AndSize(item, &str_len);
  if (str_val == NULL)
    return NULL;
  return symbol(str_val, str_len);
}

/* Parse a hex digit. Returns -1 on bad input. */
static int hex_digit(char c) {
  if (c >= '0' && c <= '9')
    return c - '0';
  if (c >= 'a' && c <= 'f')
    return 10 + (c - 'a');
  if (c >= 'A' && c <= 'F')
    return 10 + (c - 'A');
  return -1;
}

/* Parse an RFC-4122-ish GUID string into 16 bytes. Accepts hyphenated and
 * non-hyphenated forms; returns 0 on success, -1 on malformed input. */
static int parse_guid_bytes(const char *s, Py_ssize_t len, uint8_t out[16]) {
  Py_ssize_t i = 0;
  int n = 0;
  while (i < len && n < 16) {
    if (s[i] == '-') {
      i++;
      continue;
    }
    int hi = hex_digit(s[i]);
    if (hi < 0 || i + 1 >= len)
      return -1;
    int lo = hex_digit(s[i + 1]);
    if (lo < 0)
      return -1;
    out[n++] = (uint8_t)((hi << 4) | lo);
    i += 2;
  }
  if (n != 16)
    return -1;
  while (i < len) {
    if (s[i] != '-')
      return -1;
    i++;
  }
  return 0;
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

  uint8_t bytes[16];
  if (parse_guid_bytes(guid_str, guid_len, bytes) != 0) {
    Py_DECREF(guid_str_obj);
    PyErr_SetString(PyExc_RuntimeError, "init: invalid GUID format");
    return NULL;
  }

  Py_DECREF(guid_str_obj);

  obj_p ray_obj = ray_guid(bytes);
  if (ray_obj == NULL || RAY_IS_ERR(ray_obj)) {
    if (ray_obj)
      ray_release(ray_obj);
    PyErr_SetString(PyExc_RuntimeError, "init: failed to create GUID");
    return NULL;
  }
  return ray_obj;
}

/* Cast a string atom to a temporal type via ray_cast_fn. The type symbol
 * is interned on demand. Returns NULL on error (with Python exception set). */
static obj_p cast_string_to_temporal(obj_p str_obj, const char *type_name,
                                     size_t type_len) {
  obj_p type_sym = symbol(type_name, (int64_t)type_len);
  if (type_sym == NULL) {
    PyErr_Format(PyExc_RuntimeError, "init: failed to intern type symbol '%s'",
                 type_name);
    return NULL;
  }

  obj_p result = ray_cast_fn(type_sym, str_obj);
  ray_release(type_sym);

  if (result == NULL) {
    PyErr_Format(PyExc_RuntimeError, "init: failed to cast to %s", type_name);
    return NULL;
  }
  if (RAY_IS_ERR(result)) {
    PyErr_Format(PyExc_RuntimeError, "init: failed to cast to %s: %s",
                 type_name, ray_err_code(result));
    ray_release(result);
    return NULL;
  }
  return result;
}

obj_p raypy_init_date_from_py(PyObject *item) {
  PyObject *str_obj = PyObject_Str(item);
  if (str_obj == NULL)
    return NULL;

  Py_ssize_t slen;
  const char *src = PyUnicode_AsUTF8AndSize(str_obj, &slen);
  if (src == NULL) {
    Py_DECREF(str_obj);
    return NULL;
  }

  /* v2's date cast only accepts "YYYY.MM.DD" — normalize ISO "YYYY-MM-DD"
   * (the common Python form via str(datetime.date)) into the dotted form. */
  char stackbuf[64];
  char *buf = stackbuf;
  char *heapbuf = NULL;
  if ((size_t)slen + 1 > sizeof(stackbuf)) {
    heapbuf = (char *)malloc((size_t)slen + 1);
    if (heapbuf == NULL) {
      Py_DECREF(str_obj);
      PyErr_NoMemory();
      return NULL;
    }
    buf = heapbuf;
  }
  for (Py_ssize_t i = 0; i < slen; ++i) {
    buf[i] = (src[i] == '-') ? '.' : src[i];
  }
  buf[slen] = '\0';

  obj_p ray_str_obj = ray_str(buf, (size_t)slen);
  if (heapbuf)
    free(heapbuf);
  Py_DECREF(str_obj);
  if (ray_str_obj == NULL)
    return NULL;

  obj_p result = cast_string_to_temporal(ray_str_obj, "date", 4);
  ray_release(ray_str_obj);
  return result;
}

obj_p raypy_init_time_from_py(PyObject *item) {
  PyObject *str_obj = PyObject_Str(item);
  if (str_obj == NULL)
    return NULL;

  obj_p ray_str_obj = raypy_init_string_from_py(str_obj);
  Py_DECREF(str_obj);
  if (ray_str_obj == NULL)
    return NULL;

  obj_p result = cast_string_to_temporal(ray_str_obj, "time", 4);
  ray_release(ray_str_obj);
  return result;
}

obj_p raypy_init_timestamp_from_py(PyObject *item) {
  PyObject *str_obj = PyObject_Str(item);
  if (str_obj == NULL)
    return NULL;

  obj_p ray_str_obj = raypy_init_string_from_py(str_obj);
  Py_DECREF(str_obj);
  if (ray_str_obj == NULL)
    return NULL;

  obj_p result = cast_string_to_temporal(ray_str_obj, "timestamp", 9);
  ray_release(ray_str_obj);
  return result;
}

obj_p raypy_init_dict_from_py(PyObject *item) {
  if (!PyDict_Check(item))
    return NULL;

  Py_ssize_t dict_size = PyDict_Size(item);
  if (dict_size < 0)
    return NULL;

  obj_p dict_keys = ray_sym_vec_new(RAY_SYM_W64, dict_size);
  if (dict_keys == NULL || RAY_IS_ERR(dict_keys)) {
    if (dict_keys)
      ray_release(dict_keys);
    return NULL;
  }

  PyObject *py_dict_values = PyList_New(dict_size);
  if (!py_dict_values) {
    ray_release(dict_keys);
    return NULL;
  }

  PyObject *key, *val;
  Py_ssize_t pos = 0;
  Py_ssize_t idx = 0;
  int64_t *ids = (int64_t *)ray_data(dict_keys);

  while (PyDict_Next(item, &pos, &key, &val)) {
    obj_p ray_key = raypy_init_symbol_from_py(key);
    if (!ray_key) {
      Py_DECREF(py_dict_values);
      ray_release(dict_keys);
      return NULL;
    }
    ids[idx] = ray_key->i64;
    ray_release(ray_key);
    PyList_SET_ITEM(py_dict_values, idx, val);
    Py_INCREF(val);
    idx++;
  }
  dict_keys->len = dict_size;

  obj_p dict_values = raypy_init_list_from_py(py_dict_values);
  Py_DECREF(py_dict_values);
  if (!dict_values) {
    ray_release(dict_keys);
    return NULL;
  }

  obj_p result = ray_dict_fn(dict_keys, dict_values);
  ray_release(dict_keys);
  ray_release(dict_values);
  if (!result || RAY_IS_ERR(result)) {
    if (result)
      ray_release(result);
    return NULL;
  }

  return result;
}

obj_p raypy_init_list_from_py(PyObject *item) {
  if (!PyList_Check(item) && !PyTuple_Check(item))
    return NULL;

  obj_p list_vec = ray_list_new(0);
  if (list_vec == NULL || RAY_IS_ERR(list_vec)) {
    if (list_vec)
      ray_release(list_vec);
    return NULL;
  }

  if (fill_obj_from_py_sequence(&list_vec, item, 0,
                                "init: unsupported type for List item") < 0) {
    ray_release(list_vec);
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
      ray_retain(ray_obj->obj);
      return ray_obj->obj;
    }
    return NULL;
  }

  if (PyObject_HasAttrString(item, "ptr")) {
    PyObject *ptr_attr = PyObject_GetAttrString(item, "ptr");
    if (ptr_attr != NULL && PyObject_TypeCheck(ptr_attr, &RayObjectType)) {
      RayObject *ray_obj = (RayObject *)ptr_attr;
      if (ray_obj->obj != NULL) {
        ray_retain(ray_obj->obj);
        Py_XDECREF(ptr_attr);
        return ray_obj->obj;
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
    } else if (abs_type_code == RAY_STR) {
      /* RAY_STR atoms (and length-1 c8 fallback) — both produce ray_str. */
      return raypy_init_string_from_py(item);
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
