#include "rayforce_c.h"

PyObject *raypy_ser_obj(PyObject *self, PyObject *args) {
  (void)self;
  CHECK_MAIN_THREAD();

  RayObject *obj;
  if (!PyArg_ParseTuple(args, "O!", &RayObjectType, &obj))
    return NULL;

  obj_p serialized = ser_obj(obj->obj);
  if (serialized == NULL || serialized == NULL_OBJ) {
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

  obj_p deserialized = de_obj(obj->obj);
  if (deserialized == NULL || deserialized == NULL_OBJ) {
    PyErr_SetString(PyExc_RuntimeError, "serde: failed to deserialize object");
    return NULL;
  }

  if (deserialized->type == TYPE_ERR) {
    PyErr_SetString(PyExc_RuntimeError, "serde: deserialization error");
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

  if (obj->obj->type != TYPE_U8) {
    PyErr_SetString(PyExc_RuntimeError, "read: object is not a u8 vector");
    return NULL;
  }

  return PyBytes_FromStringAndSize((const char *)AS_U8(obj->obj),
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
  case TYPE_B8:
  case TYPE_U8:
    elem_size = 1;
    break;
  case TYPE_I16:
    elem_size = sizeof(i16_t);
    break;
  case TYPE_I32:
  case TYPE_DATE:
  case TYPE_TIME:
    elem_size = sizeof(i32_t);
    break;
  case TYPE_I64:
  case TYPE_TIMESTAMP:
  case TYPE_F64:
    elem_size = sizeof(i64_t);
    break;
  default:
    PyErr_SetString(PyExc_RuntimeError,
                    "read_vector_raw: unsupported vector type");
    return NULL;
  }

  return PyBytes_FromStringAndSize((const char *)AS_C8(obj->obj),
                                   obj->obj->len * elem_size);
}
