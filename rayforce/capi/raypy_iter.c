#include "rayforce_c.h"

enum vec_write_kind { VW_APPEND, VW_INSERT, VW_SET };

/* Single dispatch for LIST / RAY_STR vec / typed-scalar vec writes. `idx`
 * is ignored for VW_APPEND. On error returns NULL with PyErr set; otherwise
 * returns the new target pointer (caller must reassign). */
static ray_t *vec_write_atom(ray_t *target, int64_t idx, ray_t *atom,
                             enum vec_write_kind op, const char *op_name) {
  ray_t *result = NULL;
  if (target->type == RAY_LIST) {
    switch (op) {
    case VW_APPEND:
      result = ray_list_append(target, atom);
      break;
    case VW_INSERT:
      result = ray_list_insert_at(target, idx, atom);
      break;
    case VW_SET:
      result = ray_list_set(target, idx, atom);
      break;
    }
  } else if (target->type == RAY_STR) {
    if (atom == NULL || atom->type != -RAY_STR) {
      PyErr_SetString(PyExc_TypeError,
                      "iter: RAY_STR vector requires a string atom");
      return NULL;
    }
    const char *p = ray_str_ptr(atom);
    size_t n = ray_str_len(atom);
    switch (op) {
    case VW_APPEND:
      result = ray_str_vec_append(target, p, n);
      break;
    case VW_INSERT:
      result = ray_str_vec_insert_at(target, idx, p, n);
      break;
    case VW_SET:
      result = ray_str_vec_set(target, idx, p, n);
      break;
    }
  } else {
    scalar_scratch_t scratch;
    const void *p = atom_scalar_ptr(atom, target->type, &scratch);
    if (p == NULL) {
      PyErr_SetString(PyExc_TypeError,
                      "iter: unsupported element type for typed vector");
      return NULL;
    }
    switch (op) {
    case VW_APPEND:
      result = ray_vec_append(target, p);
      break;
    case VW_INSERT:
      result = ray_vec_insert_at(target, idx, p);
      break;
    case VW_SET:
      result = ray_vec_set(target, idx, p);
      break;
    }
  }
  if (result == NULL || RAY_IS_ERR(result)) {
    PyErr_Format(PyExc_RuntimeError, "iter: %s failed", op_name);
    return NULL;
  }
  return result;
}

PyObject *raypy_insert_obj(PyObject *self, PyObject *args) {
  (void)self;
  CHECK_MAIN_THREAD();
  RayObject *ray_obj;
  Py_ssize_t index;
  RayObject *item;

  if (!PyArg_ParseTuple(args, "O!nO!", &RayObjectType, &ray_obj, &index,
                        &RayObjectType, &item))
    return NULL;

  ray_t *target = ray_obj->obj;
  if (target == NULL) {
    PyErr_SetString(PyExc_RuntimeError, "iter: cannot insert into null object");
    return NULL;
  }
  if (index < 0 || index > target->len) {
    PyErr_SetString(PyExc_IndexError, "iter: insert index out of range");
    return NULL;
  }

  ray_t *result =
      vec_write_atom(target, (int64_t)index, item->obj, VW_INSERT, "insert");
  if (result == NULL)
    return NULL;
  ray_obj->obj = result;
  Py_RETURN_NONE;
}

PyObject *raypy_push_obj(PyObject *self, PyObject *args) {
  (void)self;
  CHECK_MAIN_THREAD();

  RayObject *ray_obj;
  RayObject *item;

  if (!PyArg_ParseTuple(args, "O!O!", &RayObjectType, &ray_obj, &RayObjectType,
                        &item))
    return NULL;

  ray_t *target = ray_obj->obj;
  if (target == NULL) {
    PyErr_SetString(PyExc_RuntimeError, "iter: cannot push to null object");
    return NULL;
  }

  ray_t *result = vec_write_atom(target, 0, item->obj, VW_APPEND, "push");
  if (result == NULL)
    return NULL;
  ray_obj->obj = result;
  Py_RETURN_NONE;
}

PyObject *raypy_set_obj(PyObject *self, PyObject *args) {
  (void)self;
  CHECK_MAIN_THREAD();

  RayObject *ray_obj;
  RayObject *idx_obj;
  RayObject *val_obj;

  if (!PyArg_ParseTuple(args, "O!O!O!", &RayObjectType, &ray_obj,
                        &RayObjectType, &idx_obj, &RayObjectType, &val_obj))
    return NULL;

  ray_t *target = ray_obj->obj;
  ray_t *idx_atom = idx_obj->obj;
  if (target == NULL || idx_atom == NULL) {
    PyErr_SetString(PyExc_RuntimeError, "iter: null target or index");
    return NULL;
  }

  /* Index must be an integer atom. */
  int64_t idx;
  if (idx_atom->type == -RAY_I64)
    idx = idx_atom->i64;
  else if (idx_atom->type == -RAY_I32)
    idx = (int64_t)idx_atom->i32;
  else if (idx_atom->type == -RAY_I16)
    idx = (int64_t)idx_atom->i16;
  else if (idx_atom->type == -RAY_U8)
    idx = (int64_t)idx_atom->u8;
  else {
    PyErr_SetString(PyExc_TypeError, "iter: index must be an integer atom");
    return NULL;
  }

  ray_t *result = vec_write_atom(target, idx, val_obj->obj, VW_SET, "set");
  if (result == NULL)
    return NULL;
  ray_obj->obj = result;
  Py_RETURN_NONE;
}
