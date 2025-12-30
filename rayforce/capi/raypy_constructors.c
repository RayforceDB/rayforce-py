#include "rayforce_c.h"

PyObject *raypy_wrap_ray_object(obj_p ray_obj) {
  if (ray_obj == NULL)
    return NULL;

  RayObject *result = (RayObject *)RayObjectType.tp_alloc(&RayObjectType, 0);
  if (result != NULL)
    result->obj = ray_obj;
  return (PyObject *)result;
}

PyObject *raypy_init_i16(PyObject *self, PyObject *args) {
  (void)self;
  CHECK_MAIN_THREAD();

  PyObject *item;
  if (!PyArg_ParseTuple(args, "O", &item))
    return NULL;

  obj_p ray_obj = raypy_init_i16_from_py(item);
  return raypy_wrap_ray_object(ray_obj);
}
PyObject *raypy_init_i32(PyObject *self, PyObject *args) {
  (void)self;
  CHECK_MAIN_THREAD();

  PyObject *item;
  if (!PyArg_ParseTuple(args, "O", &item))
    return NULL;

  obj_p ray_obj = raypy_init_i32_from_py(item);
  return raypy_wrap_ray_object(ray_obj);
}
PyObject *raypy_init_i64(PyObject *self, PyObject *args) {
  (void)self;
  CHECK_MAIN_THREAD();

  PyObject *item;
  if (!PyArg_ParseTuple(args, "O", &item))
    return NULL;

  obj_p ray_obj = raypy_init_i64_from_py(item);
  return raypy_wrap_ray_object(ray_obj);
}
PyObject *raypy_init_f64(PyObject *self, PyObject *args) {
  (void)self;
  CHECK_MAIN_THREAD();

  PyObject *item;
  if (!PyArg_ParseTuple(args, "O", &item))
    return NULL;

  obj_p ray_obj = raypy_init_f64_from_py(item);
  return raypy_wrap_ray_object(ray_obj);
}
PyObject *raypy_init_c8(PyObject *self, PyObject *args) {
  (void)self;
  CHECK_MAIN_THREAD();

  PyObject *item;
  if (!PyArg_ParseTuple(args, "O", &item))
    return NULL;

  obj_p ray_obj = raypy_init_c8_from_py(item);
  return raypy_wrap_ray_object(ray_obj);
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

  obj_p ray_obj = raypy_init_symbol_from_py(item);
  return raypy_wrap_ray_object(ray_obj);
}
PyObject *raypy_init_b8(PyObject *self, PyObject *args) {
  (void)self;
  CHECK_MAIN_THREAD();

  PyObject *item;
  if (!PyArg_ParseTuple(args, "O", &item))
    return NULL;

  obj_p ray_obj = raypy_init_b8_from_py(item);
  return raypy_wrap_ray_object(ray_obj);
}
PyObject *raypy_init_u8(PyObject *self, PyObject *args) {
  (void)self;
  CHECK_MAIN_THREAD();

  PyObject *item;
  if (!PyArg_ParseTuple(args, "O", &item))
    return NULL;

  obj_p ray_obj = raypy_init_u8_from_py(item);
  return raypy_wrap_ray_object(ray_obj);
}
PyObject *raypy_init_date(PyObject *self, PyObject *args) {
  (void)self;
  CHECK_MAIN_THREAD();

  PyObject *item;
  if (!PyArg_ParseTuple(args, "O", &item))
    return NULL;

  obj_p ray_obj = raypy_init_date_from_py(item);
  return raypy_wrap_ray_object(ray_obj);
}
PyObject *raypy_init_time(PyObject *self, PyObject *args) {
  (void)self;
  CHECK_MAIN_THREAD();

  PyObject *item;
  if (!PyArg_ParseTuple(args, "O", &item))
    return NULL;

  obj_p ray_obj = raypy_init_time_from_py(item);
  return raypy_wrap_ray_object(ray_obj);
}
PyObject *raypy_init_timestamp(PyObject *self, PyObject *args) {
  (void)self;
  CHECK_MAIN_THREAD();

  PyObject *item;
  if (!PyArg_ParseTuple(args, "O", &item))
    return NULL;

  obj_p ray_obj = raypy_init_timestamp_from_py(item);
  return raypy_wrap_ray_object(ray_obj);
}
PyObject *raypy_init_guid(PyObject *self, PyObject *args) {
  (void)self;
  CHECK_MAIN_THREAD();

  PyObject *item;
  if (!PyArg_ParseTuple(args, "O", &item))
    return NULL;

  obj_p ray_obj = raypy_init_guid_from_py(item);
  return raypy_wrap_ray_object(ray_obj);
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
