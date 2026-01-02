#include "rayforce_c.h"

PyObject *raypy_hopen(PyObject *self, PyObject *args) {
  (void)self;
  CHECK_MAIN_THREAD();

  RayObject *path_obj;
  RayObject *timeout_obj = NULL;

  if (!PyArg_ParseTuple(args, "O!|O!", &RayObjectType, &path_obj,
                        &RayObjectType, &timeout_obj)) {
    return NULL;
  }

  obj_p ray_obj = timeout_obj
                      ? ray_hopen((obj_p[]){path_obj->obj, timeout_obj->obj}, 2)
                      : ray_hopen((obj_p[]){path_obj->obj}, 1);

  if (ray_obj == NULL) {
    PyErr_SetString(PyExc_RuntimeError, "io: failed to open handle");
    return NULL;
  }
  return raypy_wrap_ray_object(ray_obj);
}

PyObject *raypy_hclose(PyObject *self, PyObject *args) {
  (void)self;
  CHECK_MAIN_THREAD();

  RayObject *handle_obj;

  if (!PyArg_ParseTuple(args, "O!", &RayObjectType, &handle_obj))
    return NULL;

  obj_p ray_obj = ray_hclose(handle_obj->obj);
  if (ray_obj == NULL) {
    PyErr_SetString(PyExc_RuntimeError, "io: failed to close handle");
    return NULL;
  }
  return raypy_wrap_ray_object(ray_obj);
}
PyObject *raypy_write(PyObject *self, PyObject *args) {
  (void)self;
  CHECK_MAIN_THREAD();

  RayObject *handle_obj;
  RayObject *data_obj;

  if (!PyArg_ParseTuple(args, "O!O!", &RayObjectType, &handle_obj,
                        &RayObjectType, &data_obj))
    return NULL;

  obj_p ray_obj = ray_write(handle_obj->obj, data_obj->obj);
  if (ray_obj == NULL) {
    PyErr_SetString(PyExc_RuntimeError, "io: failed to write data");
    return NULL;
  }
  return raypy_wrap_ray_object(ray_obj);
}
