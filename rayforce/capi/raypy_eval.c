#include "rayforce_c.h"

PyObject *raypy_eval_str(PyObject *self, PyObject *args) {
  (void)self;
  CHECK_MAIN_THREAD();
  RayObject *item;

  if (!PyArg_ParseTuple(args, "O!", &RayObjectType, &item))
    return NULL;

  if (item->obj == NULL || item->obj->type != -RAY_STR) {
    PyErr_SetString(PyExc_RuntimeError, "eval: argument must be a string atom");
    return NULL;
  }

  const char *src = ray_str_ptr(item->obj);
  ray_t *ray_obj = ray_eval_str(src);
  if (ray_obj == NULL) {
    PyErr_SetString(PyExc_RuntimeError,
                    "eval: failed to evaluate string expression");
    return NULL;
  }
  /* If ray_obj is RAY_ERROR, still wrap it — the Python error_handler maps
   * ray_error "code" → RayforceTypeError/DomainError/LengthError/etc. */
  return raypy_wrap_ray_object(ray_obj);
}
PyObject *raypy_eval_obj(PyObject *self, PyObject *args) {
  (void)self;
  CHECK_MAIN_THREAD();
  RayObject *item;

  if (!PyArg_ParseTuple(args, "O!", &RayObjectType, &item))
    return NULL;

  ray_t *ray_obj = ray_eval(item->obj);
  if (ray_obj == NULL) {
    PyErr_SetString(PyExc_RuntimeError, "eval: failed to evaluate object");
    return NULL;
  }
  return raypy_wrap_ray_object(ray_obj);
}
