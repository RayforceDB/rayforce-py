#include "rayforce_c.h"

PyObject *raypy_read_i16(PyObject *self, PyObject *args) {
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
PyObject *raypy_read_i32(PyObject *self, PyObject *args) {
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
PyObject *raypy_read_i64(PyObject *self, PyObject *args) {
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
PyObject *raypy_read_f64(PyObject *self, PyObject *args) {
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
PyObject *raypy_read_c8(PyObject *self, PyObject *args) {
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
PyObject *raypy_read_string(PyObject *self, PyObject *args) {
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
PyObject *raypy_read_symbol(PyObject *self, PyObject *args) {
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
PyObject *raypy_read_b8(PyObject *self, PyObject *args) {
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
PyObject *raypy_read_u8(PyObject *self, PyObject *args) {
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
PyObject *raypy_read_date(PyObject *self, PyObject *args) {
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
PyObject *raypy_read_time(PyObject *self, PyObject *args) {
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
PyObject *raypy_read_timestamp(PyObject *self, PyObject *args) {
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
PyObject *raypy_read_guid(PyObject *self, PyObject *args) {
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
