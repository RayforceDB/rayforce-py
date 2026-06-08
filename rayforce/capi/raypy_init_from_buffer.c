#include "rayforce_c.h"

/* Apply an Arrow validity bitmap (1=valid, 0=null) to `vec` by setting null
 * bits for entries whose bitmap position is zero. */
static void apply_null_bitmap(ray_t *vec, const unsigned char *bitmap,
                              Py_ssize_t length) {
  for (Py_ssize_t i = 0; i < length; i++) {
    if (!(bitmap[(size_t)i / 8] & (1u << ((size_t)i % 8))))
      ray_vec_set_null(vec, i, true);
  }
}

/* Pull Arrow's (null_bitmap, offsets, data) trio of buffers from a PyArrow
 * Array's `buffers()` sequence. On success returns 0 with `null_bitmap_py`
 * owned by the caller (may be Py_None) and the two Py_buffers populated.
 * On failure returns -1 with PyErr set and nothing to clean up. */
static int acquire_arrow_string_buffers(PyObject *buffers,
                                        PyObject **null_bitmap_py,
                                        Py_buffer *offsets_view,
                                        Py_buffer *data_view) {
  PyObject *offsets_py = PySequence_GetItem(buffers, 1);
  PyObject *data_py = PySequence_GetItem(buffers, 2);
  *null_bitmap_py = PySequence_GetItem(buffers, 0);
  if (offsets_py == NULL || data_py == NULL) {
    Py_XDECREF(*null_bitmap_py);
    Py_XDECREF(offsets_py);
    Py_XDECREF(data_py);
    return -1;
  }
  if (PyObject_GetBuffer(offsets_py, offsets_view, PyBUF_SIMPLE) < 0) {
    Py_DECREF(offsets_py);
    Py_DECREF(data_py);
    Py_XDECREF(*null_bitmap_py);
    return -1;
  }
  Py_DECREF(offsets_py);
  if (PyObject_GetBuffer(data_py, data_view, PyBUF_SIMPLE) < 0) {
    PyBuffer_Release(offsets_view);
    Py_DECREF(data_py);
    Py_XDECREF(*null_bitmap_py);
    return -1;
  }
  Py_DECREF(data_py);
  return 0;
}

/* Pull Arrow's (null_bitmap, data) pair from a PyArrow Array's `buffers()`
 * sequence — fixed-width numeric/boolean form. Mirrors
 * acquire_arrow_string_buffers; same ownership contract. */
static int acquire_arrow_data_buffer(PyObject *buffers,
                                     PyObject **null_bitmap_py,
                                     Py_buffer *data_view) {
  PyObject *data_py = PySequence_GetItem(buffers, 1);
  *null_bitmap_py = PySequence_GetItem(buffers, 0);
  if (data_py == NULL) {
    Py_XDECREF(*null_bitmap_py);
    return -1;
  }
  if (PyObject_GetBuffer(data_py, data_view, PyBUF_SIMPLE) < 0) {
    Py_DECREF(data_py);
    Py_XDECREF(*null_bitmap_py);
    return -1;
  }
  Py_DECREF(data_py);
  return 0;
}

/* Apply an optional Arrow validity bitmap held in a PyObject. No-op if py
 * is NULL or Py_None. */
static void apply_optional_null_bitmap_py(ray_t *vec, PyObject *py,
                                          Py_ssize_t length) {
  if (py == NULL || py == Py_None)
    return;
  Py_buffer view;
  if (PyObject_GetBuffer(py, &view, PyBUF_SIMPLE) < 0) {
    PyErr_Clear();
    return;
  }
  apply_null_bitmap(vec, (const unsigned char *)view.buf, length);
  PyBuffer_Release(&view);
}

PyObject *raypy_init_vector_from_buffer(PyObject *self, PyObject *args) {
  (void)self;
  CHECK_MAIN_THREAD();

  int type_code;
  Py_ssize_t length;
  PyObject *buffer_obj;
  PyObject *null_bitmap_obj = NULL;

  if (!PyArg_ParseTuple(args, "inO|O", &type_code, &length, &buffer_obj,
                        &null_bitmap_obj))
    return NULL;

  if (length < 0) {
    PyErr_SetString(PyExc_ValueError, "length must be non-negative");
    return NULL;
  }

  Py_buffer buffer_view;
  if (PyObject_GetBuffer(buffer_obj, &buffer_view, PyBUF_SIMPLE) < 0) {
    return NULL;
  }

  int vector_type_code = ray_abs_type(type_code);
  size_t element_size = ray_scalar_elem_size((int8_t)vector_type_code);
  if (element_size == 0 || vector_type_code == RAY_GUID) {
    PyBuffer_Release(&buffer_view);
    PyErr_SetString(PyExc_ValueError, "Unsupported type code for buffer");
    return NULL;
  }

  size_t expected_size = (size_t)length * element_size;
  if ((size_t)buffer_view.len < expected_size) {
    PyBuffer_Release(&buffer_view);
    PyErr_SetString(PyExc_ValueError, "Buffer too small for given length");
    return NULL;
  }

  ray_t *ray_obj = ray_vec_new((int8_t)vector_type_code, (int64_t)length);
  if (ray_obj == NULL || RAY_IS_ERR(ray_obj)) {
    if (ray_obj)
      ray_release(ray_obj);
    PyBuffer_Release(&buffer_view);
    PyErr_SetString(PyExc_RuntimeError, "Failed to create vector");
    return NULL;
  }

  int has_nulls = (null_bitmap_obj != NULL && null_bitmap_obj != Py_None);

  Py_buffer null_bitmap_view = {0};
  if (has_nulls) {
    if (PyObject_GetBuffer(null_bitmap_obj, &null_bitmap_view, PyBUF_SIMPLE) <
        0) {
      ray_release(ray_obj);
      PyBuffer_Release(&buffer_view);
      return NULL;
    }
    size_t min_bitmap_size = ((size_t)length + 7) / 8;
    if ((size_t)null_bitmap_view.len < min_bitmap_size) {
      ray_release(ray_obj);
      PyBuffer_Release(&null_bitmap_view);
      PyBuffer_Release(&buffer_view);
      PyErr_SetString(PyExc_ValueError, "Null bitmap too small");
      return NULL;
    }
  }

  /* Bulk copy then mark nulls — saves per-row branching. */
  memcpy(ray_data(ray_obj), buffer_view.buf, expected_size);
  ray_obj->len = length;

  if (has_nulls)
    apply_null_bitmap(ray_obj, (const unsigned char *)null_bitmap_view.buf,
                      length);

  PyBuffer_Release(&buffer_view);
  if (has_nulls)
    PyBuffer_Release(&null_bitmap_view);

  return raypy_wrap_ray_object(ray_obj);
}

// Bulk memcpy from raw buffer (numpy arrays, bytes, etc.)
PyObject *raypy_init_vector_from_raw_buffer(PyObject *self, PyObject *args) {
  (void)self;
  CHECK_MAIN_THREAD();

  int type_code;
  Py_ssize_t length;
  PyObject *buffer_obj;

  if (!PyArg_ParseTuple(args, "inO", &type_code, &length, &buffer_obj))
    return NULL;

  if (length < 0) {
    PyErr_SetString(PyExc_ValueError, "length must be non-negative");
    return NULL;
  }

  int vector_type_code = ray_abs_type(type_code);

  if (length == 0) {
    ray_t *ray_obj = ray_vec_new((int8_t)vector_type_code, 0);
    if (ray_obj == NULL || RAY_IS_ERR(ray_obj)) {
      if (ray_obj)
        ray_release(ray_obj);
      PyErr_SetString(PyExc_RuntimeError, "Failed to create empty vector");
      return NULL;
    }
    return raypy_wrap_ray_object(ray_obj);
  }

  Py_buffer buffer_view;
  if (PyObject_GetBuffer(buffer_obj, &buffer_view, PyBUF_SIMPLE) < 0) {
    return NULL;
  }

  size_t element_size = ray_scalar_elem_size((int8_t)vector_type_code);
  if (element_size == 0 || vector_type_code == RAY_GUID) {
    PyBuffer_Release(&buffer_view);
    PyErr_SetString(PyExc_ValueError,
                    "Unsupported type code for raw buffer init");
    return NULL;
  }

  size_t expected_size = (size_t)length * element_size;
  if ((size_t)buffer_view.len < expected_size) {
    PyBuffer_Release(&buffer_view);
    PyErr_SetString(PyExc_ValueError, "Buffer too small for given length");
    return NULL;
  }

  ray_t *ray_obj = ray_vec_new((int8_t)vector_type_code, (int64_t)length);
  if (ray_obj == NULL || RAY_IS_ERR(ray_obj)) {
    if (ray_obj)
      ray_release(ray_obj);
    PyBuffer_Release(&buffer_view);
    PyErr_SetString(PyExc_RuntimeError, "Failed to create vector");
    return NULL;
  }

  memcpy(ray_data(ray_obj), buffer_view.buf, expected_size);
  ray_obj->len = length;

  PyBuffer_Release(&buffer_view);
  return raypy_wrap_ray_object(ray_obj);
}

// Zero-copy API for Arrow buffers
PyObject *raypy_init_vector_from_arrow_array(PyObject *self, PyObject *args) {
  (void)self;
  CHECK_MAIN_THREAD();

  int type_code;
  PyObject *arrow_array_obj;

  if (!PyArg_ParseTuple(args, "iO", &type_code, &arrow_array_obj))
    return NULL;

  int vector_type_code = ray_abs_type(type_code);

  // Get buffers() method from PyArrow Array
  PyObject *buffers_method = PyObject_GetAttrString(arrow_array_obj, "buffers");
  if (buffers_method == NULL) {
    PyErr_SetString(PyExc_TypeError,
                    "Arrow array object must have buffers() method");
    return NULL;
  }

  PyObject *buffers = PyObject_CallObject(buffers_method, NULL);
  Py_DECREF(buffers_method);
  if (buffers == NULL) {
    return NULL;
  }

  Py_ssize_t num_buffers = PySequence_Size(buffers);
  if (!PySequence_Check(buffers) || num_buffers < 2) {
    Py_DECREF(buffers);
    PyErr_SetString(
        PyExc_ValueError,
        "Arrow array must have at least 2 buffers (null bitmap and data)");
    return NULL;
  }

  if (vector_type_code == RAY_SYM) {
    if (num_buffers < 3) {
      Py_DECREF(buffers);
      PyErr_SetString(PyExc_ValueError, "Invalid Arrow string buffer");
      return NULL;
    }
    Py_ssize_t length = PyObject_Length(arrow_array_obj);
    if (length < 0) {
      Py_DECREF(buffers);
      return NULL;
    }

    PyObject *null_bitmap_py;
    Py_buffer offsets_view, data_view;
    int rc = acquire_arrow_string_buffers(buffers, &null_bitmap_py,
                                          &offsets_view, &data_view);
    Py_DECREF(buffers);
    if (rc < 0)
      return NULL;

    const int32_t *offsets = (const int32_t *)offsets_view.buf;
    const char *data = (const char *)data_view.buf;
    ray_t *ray_obj = ray_sym_vec_new(RAY_SYM_W64, (int64_t)length);
    if (ray_obj == NULL || RAY_IS_ERR(ray_obj)) {
      if (ray_obj)
        ray_release(ray_obj);
      PyBuffer_Release(&offsets_view);
      PyBuffer_Release(&data_view);
      Py_XDECREF(null_bitmap_py);
      PyErr_SetString(PyExc_RuntimeError, "Failed to create vector");
      return NULL;
    }

    int64_t *ids = (int64_t *)ray_data(ray_obj);
    for (Py_ssize_t i = 0; i < length; i++) {
      int64_t id = ray_sym_intern(data + offsets[i],
                                  (size_t)(offsets[i + 1] - offsets[i]));
      if (id < 0) {
        ray_release(ray_obj);
        PyBuffer_Release(&offsets_view);
        PyBuffer_Release(&data_view);
        Py_XDECREF(null_bitmap_py);
        PyErr_SetString(PyExc_RuntimeError,
                        "Failed to intern symbol from arrow data");
        return NULL;
      }
      ids[i] = id;
    }
    ray_obj->len = length;

    apply_optional_null_bitmap_py(ray_obj, null_bitmap_py, length);
    PyBuffer_Release(&offsets_view);
    PyBuffer_Release(&data_view);
    Py_XDECREF(null_bitmap_py);
    return raypy_wrap_ray_object(ray_obj);
  }

  if (vector_type_code == RAY_STR) {
    if (num_buffers < 3) {
      Py_DECREF(buffers);
      PyErr_SetString(PyExc_ValueError, "Invalid Arrow string buffer");
      return NULL;
    }
    Py_ssize_t length = PyObject_Length(arrow_array_obj);
    if (length < 0) {
      Py_DECREF(buffers);
      return NULL;
    }

    PyObject *null_bitmap_py;
    Py_buffer offsets_view, data_view;
    int rc = acquire_arrow_string_buffers(buffers, &null_bitmap_py,
                                          &offsets_view, &data_view);
    Py_DECREF(buffers);
    if (rc < 0)
      return NULL;

    const int32_t *offsets = (const int32_t *)offsets_view.buf;
    const char *data = (const char *)data_view.buf;
    ray_t *ray_obj = ray_vec_new(RAY_STR, (int64_t)length);
    if (ray_obj == NULL || RAY_IS_ERR(ray_obj)) {
      if (ray_obj)
        ray_release(ray_obj);
      PyBuffer_Release(&offsets_view);
      PyBuffer_Release(&data_view);
      Py_XDECREF(null_bitmap_py);
      PyErr_SetString(PyExc_RuntimeError, "Failed to create string vector");
      return NULL;
    }

    for (Py_ssize_t i = 0; i < length; i++) {
      ray_obj = ray_str_vec_append(ray_obj, data + offsets[i],
                                   (size_t)(offsets[i + 1] - offsets[i]));
      if (ray_obj == NULL || RAY_IS_ERR(ray_obj)) {
        if (ray_obj)
          ray_release(ray_obj);
        PyBuffer_Release(&offsets_view);
        PyBuffer_Release(&data_view);
        Py_XDECREF(null_bitmap_py);
        PyErr_SetString(PyExc_RuntimeError, "Failed to append string");
        return NULL;
      }
    }

    apply_optional_null_bitmap_py(ray_obj, null_bitmap_py, length);
    PyBuffer_Release(&offsets_view);
    PyBuffer_Release(&data_view);
    Py_XDECREF(null_bitmap_py);
    return raypy_wrap_ray_object(ray_obj);
  }

  Py_ssize_t length = PyObject_Length(arrow_array_obj);
  if (length < 0) {
    Py_DECREF(buffers);
    return NULL;
  }

  PyObject *null_bitmap_py;
  Py_buffer data_view;
  int rc = acquire_arrow_data_buffer(buffers, &null_bitmap_py, &data_view);
  Py_DECREF(buffers);
  if (rc < 0)
    return NULL;

  size_t element_size = ray_scalar_elem_size((int8_t)vector_type_code);
  if (element_size == 0 || vector_type_code == RAY_GUID) {
    PyBuffer_Release(&data_view);
    Py_XDECREF(null_bitmap_py);
    PyErr_SetString(PyExc_ValueError,
                    "Unsupported type code for Arrow array conversion");
    return NULL;
  }

  int is_boolean_bitmap = (vector_type_code == RAY_BOOL);
  size_t expected_size = is_boolean_bitmap ? ((size_t)length + 7) / 8
                                           : (size_t)length * element_size;

  if ((size_t)data_view.len < expected_size) {
    PyBuffer_Release(&data_view);
    Py_XDECREF(null_bitmap_py);
    PyErr_SetString(PyExc_ValueError, "Arrow data buffer too small");
    return NULL;
  }

  ray_t *ray_obj = ray_vec_new((int8_t)vector_type_code, (int64_t)length);
  if (ray_obj == NULL || RAY_IS_ERR(ray_obj)) {
    if (ray_obj)
      ray_release(ray_obj);
    PyBuffer_Release(&data_view);
    Py_XDECREF(null_bitmap_py);
    PyErr_SetString(PyExc_RuntimeError, "Failed to create vector");
    return NULL;
  }

  if (is_boolean_bitmap) {
    const unsigned char *bitmap = (const unsigned char *)data_view.buf;
    unsigned char *bytes = (unsigned char *)ray_data(ray_obj);
    for (Py_ssize_t i = 0; i < length; i++)
      bytes[i] = (bitmap[(size_t)i / 8] >> ((size_t)i % 8)) & 1u;
  } else {
    memcpy(ray_data(ray_obj), data_view.buf, expected_size);
  }
  ray_obj->len = length;

  apply_optional_null_bitmap_py(ray_obj, null_bitmap_py, length);
  PyBuffer_Release(&data_view);
  Py_XDECREF(null_bitmap_py);
  return raypy_wrap_ray_object(ray_obj);
}
