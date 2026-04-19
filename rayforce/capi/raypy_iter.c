#include "rayforce_c.h"

typedef union {
  uint8_t u8;
  int16_t i16;
  int32_t i32;
  int64_t i64;
  double f64;
} scalar_scratch_t;

/* Extract a raw scalar payload from an atom for ray_vec_append/set.
 * Returns a pointer into the supplied scratch buffer (caller-owned) and
 * sets *out_size to the element width.  Returns NULL if the atom type
 * cannot be coerced into the target vector's element width. */
static const void *atom_scalar_ptr(obj_p atom, int8_t vec_type,
                                   scalar_scratch_t *scratch,
                                   size_t *out_size) {
  switch (vec_type) {
  case RAY_BOOL:
  case RAY_U8:
    scratch->u8 = atom->u8;
    *out_size = 1;
    return &scratch->u8;
  case RAY_I16:
    scratch->i16 = atom->i16;
    *out_size = 2;
    return &scratch->i16;
  case RAY_I32:
  case RAY_DATE:
  case RAY_TIME:
    scratch->i32 = atom->i32;
    *out_size = 4;
    return &scratch->i32;
  case RAY_I64:
  case RAY_TIMESTAMP:
  case RAY_SYM:
    scratch->i64 = atom->i64;
    *out_size = 8;
    return &scratch->i64;
  case RAY_F64:
    scratch->f64 = atom->f64;
    *out_size = 8;
    return &scratch->f64;
  default:
    return NULL;
  }
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

  obj_p target = ray_obj->obj;
  if (target == NULL || target->type != RAY_LIST) {
    PyErr_SetString(PyExc_NotImplementedError,
                    "iter: insert is only supported on lists in v2");
    return NULL;
  }

  int64_t old_len = target->len;
  if (index < 0 || index > old_len) {
    PyErr_SetString(PyExc_IndexError, "iter: insert index out of range");
    return NULL;
  }

  /* Build a new list of length old_len+1 with item spliced at index. */
  obj_p new_list = ray_list_new(old_len + 1);
  if (new_list == NULL || RAY_IS_ERR(new_list)) {
    PyErr_SetString(PyExc_RuntimeError,
                    "iter: failed to allocate new list for insert");
    if (new_list)
      ray_release(new_list);
    return NULL;
  }

  ray_t **src = (ray_t **)ray_data(target);
  for (int64_t i = 0; i < (int64_t)index; ++i) {
    obj_p next = ray_list_append(new_list, src[i]);
    if (next == NULL || RAY_IS_ERR(next)) {
      ray_release(new_list);
      PyErr_SetString(PyExc_RuntimeError, "iter: list append failed");
      return NULL;
    }
    new_list = next;
  }
  {
    obj_p next = ray_list_append(new_list, item->obj);
    if (next == NULL || RAY_IS_ERR(next)) {
      ray_release(new_list);
      PyErr_SetString(PyExc_RuntimeError, "iter: list append failed");
      return NULL;
    }
    new_list = next;
  }
  for (int64_t i = (int64_t)index; i < old_len; ++i) {
    obj_p next = ray_list_append(new_list, src[i]);
    if (next == NULL || RAY_IS_ERR(next)) {
      ray_release(new_list);
      PyErr_SetString(PyExc_RuntimeError, "iter: list append failed");
      return NULL;
    }
    new_list = next;
  }

  ray_release(target);
  ray_obj->obj = new_list;
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

  obj_p target = ray_obj->obj;
  if (target == NULL) {
    PyErr_SetString(PyExc_RuntimeError, "iter: cannot push to null object");
    return NULL;
  }

  if (target->type == RAY_LIST) {
    obj_p result = ray_list_append(target, item->obj);
    if (result == NULL || RAY_IS_ERR(result)) {
      PyErr_SetString(PyExc_RuntimeError, "iter: failed to push object");
      return NULL;
    }
    ray_obj->obj = result;
    Py_RETURN_NONE;
  }

  if (target->type == RAY_STR) {
    if (item->obj == NULL || item->obj->type != -RAY_STR) {
      PyErr_SetString(PyExc_TypeError,
                      "iter: RAY_STR vector requires a string atom");
      return NULL;
    }
    obj_p result = ray_str_vec_append(target, ray_str_ptr(item->obj),
                                      ray_str_len(item->obj));
    if (result == NULL || RAY_IS_ERR(result)) {
      PyErr_SetString(PyExc_RuntimeError, "iter: failed to append string");
      return NULL;
    }
    ray_obj->obj = result;
    Py_RETURN_NONE;
  }

  /* Typed scalar vector — extract raw scalar from atom and append. */
  scalar_scratch_t scratch;
  size_t esz = 0;
  const void *p = atom_scalar_ptr(item->obj, target->type, &scratch, &esz);
  if (p == NULL) {
    PyErr_SetString(PyExc_TypeError,
                    "iter: unsupported element type for typed vector");
    return NULL;
  }
  obj_p result = ray_vec_append(target, p);
  if (result == NULL || RAY_IS_ERR(result)) {
    PyErr_SetString(PyExc_RuntimeError, "iter: failed to push scalar");
    return NULL;
  }
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

  obj_p target = ray_obj->obj;
  obj_p idx_atom = idx_obj->obj;
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

  if (target->type == RAY_LIST) {
    obj_p result = ray_list_set(target, idx, val_obj->obj);
    if (result == NULL || RAY_IS_ERR(result)) {
      PyErr_SetString(PyExc_RuntimeError, "iter: failed to set list element");
      return NULL;
    }
    ray_obj->obj = result;
    Py_RETURN_NONE;
  }

  if (target->type == RAY_STR) {
    if (val_obj->obj == NULL || val_obj->obj->type != -RAY_STR) {
      PyErr_SetString(PyExc_TypeError,
                      "iter: RAY_STR vector requires a string atom");
      return NULL;
    }
    obj_p result = ray_str_vec_set(target, idx, ray_str_ptr(val_obj->obj),
                                   ray_str_len(val_obj->obj));
    if (result == NULL || RAY_IS_ERR(result)) {
      PyErr_SetString(PyExc_RuntimeError, "iter: failed to set string element");
      return NULL;
    }
    ray_obj->obj = result;
    Py_RETURN_NONE;
  }

  scalar_scratch_t scratch;
  size_t esz = 0;
  const void *p = atom_scalar_ptr(val_obj->obj, target->type, &scratch, &esz);
  if (p == NULL) {
    PyErr_SetString(PyExc_TypeError,
                    "iter: unsupported element type for typed vector");
    return NULL;
  }
  obj_p result = ray_vec_set(target, idx, p);
  if (result == NULL || RAY_IS_ERR(result)) {
    PyErr_SetString(PyExc_RuntimeError, "iter: failed to set scalar element");
    return NULL;
  }
  ray_obj->obj = result;
  Py_RETURN_NONE;
}
