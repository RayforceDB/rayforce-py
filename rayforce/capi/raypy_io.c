#include "rayforce_c.h"

PyObject *raypy_hopen(PyObject *self, PyObject *args) {
  (void)self;
  CHECK_MAIN_THREAD();
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

  obj_p ray_obj = ray_hopen(ray_args, arg_count);
  if (ray_obj == NULL) {
    PyErr_SetString(PyExc_RuntimeError, "Failed to open handle");
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
    PyErr_SetString(PyExc_RuntimeError, "Failed to close handle");
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
    PyErr_SetString(PyExc_RuntimeError, "Failed to write data");
    return NULL;
  }
  return raypy_wrap_ray_object(ray_obj);
}
