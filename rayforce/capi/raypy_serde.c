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
