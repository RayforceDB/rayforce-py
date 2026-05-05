#include "rayforce_c.h"

PyObject *raypy_ser_obj(PyObject *self, PyObject *args) {
  (void)self;
  CHECK_MAIN_THREAD();

  RayObject *obj;
  if (!PyArg_ParseTuple(args, "O!", &RayObjectType, &obj))
    return NULL;

  ray_t *serialized = ray_ser(obj->obj);
  if (serialized == NULL || serialized == RAY_NULL_OBJ) {
    PyErr_SetString(PyExc_RuntimeError, "serde: failed to serialize object");
    return NULL;
  }

  return raypy_wrap_ray_object(serialized);
}

PyObject *raypy_de_obj(PyObject *self, PyObject *args) {
  (void)self;
  CHECK_MAIN_THREAD();

  RayObject *obj;
  if (!PyArg_ParseTuple(args, "O!", &RayObjectType, &obj))
    return NULL;

  ray_t *deserialized = ray_de(obj->obj);
  if (deserialized == NULL || deserialized == RAY_NULL_OBJ) {
    PyErr_SetString(PyExc_RuntimeError, "serde: failed to deserialize object");
    return NULL;
  }

  if (RAY_IS_ERR(deserialized)) {
    PyErr_Format(PyExc_RuntimeError, "serde: deserialization error: %s",
                 ray_err_code(deserialized));
    ray_release(deserialized);
    return NULL;
  }

  return raypy_wrap_ray_object(deserialized);
}

PyObject *raypy_read_u8_vector(PyObject *self, PyObject *args) {
  (void)self;
  CHECK_MAIN_THREAD();

  RayObject *obj;
  if (!PyArg_ParseTuple(args, "O!", &RayObjectType, &obj))
    return NULL;

  if (obj->obj->type != RAY_U8) {
    PyErr_SetString(PyExc_RuntimeError, "read: object is not a u8 vector");
    return NULL;
  }

  return PyBytes_FromStringAndSize((const char *)ray_data(obj->obj),
                                   obj->obj->len);
}
PyObject *raypy_read_vector_raw(PyObject *self, PyObject *args) {
  (void)self;
  CHECK_MAIN_THREAD();

  RayObject *obj;
  if (!PyArg_ParseTuple(args, "O!", &RayObjectType, &obj))
    return NULL;

  size_t elem_size;
  switch (obj->obj->type) {
  case RAY_BOOL:
  case RAY_U8:
    elem_size = 1;
    break;
  case RAY_I16:
    elem_size = sizeof(int16_t);
    break;
  case RAY_I32:
  case RAY_DATE:
  case RAY_TIME:
  case RAY_F32:
    elem_size = sizeof(int32_t);
    break;
  case RAY_I64:
  case RAY_TIMESTAMP:
  case RAY_F64:
    elem_size = sizeof(int64_t);
    break;
  default:
    PyErr_SetString(PyExc_RuntimeError,
                    "read_vector_raw: unsupported vector type");
    return NULL;
  }

  return PyBytes_FromStringAndSize((const char *)ray_data(obj->obj),
                                   obj->obj->len * elem_size);
}
