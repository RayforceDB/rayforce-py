#include "rayforce_c.h"

/* Helper: width in bytes for the typed vector element. Returns 0 if the
 * type isn't supported by the buffer-init path. */
static size_t scalar_elem_size(int vector_type_code) {
  switch (vector_type_code) {
  case RAY_BOOL:
  case RAY_U8:
    return 1;
  case RAY_I16:
    return 2;
  case RAY_I32:
  case RAY_DATE:
  case RAY_TIME:
  case RAY_F32:
    return 4;
  case RAY_I64:
  case RAY_F64:
  case RAY_TIMESTAMP:
    return 8;
  case RAY_GUID:
    return 16;
  default:
    return 0;
  }
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

  int vector_type_code = type_code < 0 ? -type_code : type_code;
  size_t element_size = scalar_elem_size(vector_type_code);
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

  obj_p ray_obj = ray_vec_new((int8_t)vector_type_code, (int64_t)length);
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

  if (has_nulls) {
    const unsigned char *bitmap = (const unsigned char *)null_bitmap_view.buf;
    for (Py_ssize_t i = 0; i < length; i++) {
      size_t byte_idx = (size_t)i / 8;
      size_t bit_idx = (size_t)i % 8;
      if (!(bitmap[byte_idx] & (1u << bit_idx))) {
        ray_vec_set_null(ray_obj, i, true);
      }
    }
  }

  PyBuffer_Release(&buffer_view);
  if (has_nulls) {
    PyBuffer_Release(&null_bitmap_view);
  }

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

  int vector_type_code = type_code < 0 ? -type_code : type_code;

  if (length == 0) {
    obj_p ray_obj = ray_vec_new((int8_t)vector_type_code, 0);
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

  size_t element_size = scalar_elem_size(vector_type_code);
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

  obj_p ray_obj = ray_vec_new((int8_t)vector_type_code, (int64_t)length);
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

  int vector_type_code = type_code < 0 ? -type_code : type_code;

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

    // buffers[0] = null bitmap, buffers[1] = offsets, buffers[2] = data
    PyObject *null_bitmap_py = PySequence_GetItem(buffers, 0);
    PyObject *offsets_buffer_py = PySequence_GetItem(buffers, 1);
    PyObject *data_buffer_py = PySequence_GetItem(buffers, 2);
    Py_DECREF(buffers);

    if (offsets_buffer_py == NULL || data_buffer_py == NULL) {
      if (null_bitmap_py != NULL)
        Py_DECREF(null_bitmap_py);
      if (offsets_buffer_py != NULL)
        Py_DECREF(offsets_buffer_py);
      if (data_buffer_py != NULL)
        Py_DECREF(data_buffer_py);
      return NULL;
    }

    Py_buffer offsets_buffer_view;
    if (PyObject_GetBuffer(offsets_buffer_py, &offsets_buffer_view,
                           PyBUF_SIMPLE) < 0) {
      Py_DECREF(offsets_buffer_py);
      Py_DECREF(data_buffer_py);
      if (null_bitmap_py != NULL)
        Py_DECREF(null_bitmap_py);
      return NULL;
    }
    Py_DECREF(offsets_buffer_py);

    Py_buffer data_buffer_view;
    if (PyObject_GetBuffer(data_buffer_py, &data_buffer_view, PyBUF_SIMPLE) <
        0) {
      PyBuffer_Release(&offsets_buffer_view);
      Py_DECREF(data_buffer_py);
      if (null_bitmap_py != NULL)
        Py_DECREF(null_bitmap_py);
      return NULL;
    }
    Py_DECREF(data_buffer_py);

    const int32_t *offsets = (const int32_t *)offsets_buffer_view.buf;
    const char *data = (const char *)data_buffer_view.buf;

    obj_p ray_obj = ray_sym_vec_new(RAY_SYM_W64, (int64_t)length);
    if (ray_obj == NULL || RAY_IS_ERR(ray_obj)) {
      if (ray_obj)
        ray_release(ray_obj);
      PyBuffer_Release(&offsets_buffer_view);
      PyBuffer_Release(&data_buffer_view);
      if (null_bitmap_py != NULL)
        Py_DECREF(null_bitmap_py);
      PyErr_SetString(PyExc_RuntimeError, "Failed to create vector");
      return NULL;
    }

    int64_t *ids = (int64_t *)ray_data(ray_obj);
    for (Py_ssize_t i = 0; i < length; i++) {
      int32_t start = offsets[i];
      int32_t end = offsets[i + 1];
      int32_t str_len = end - start;

      int64_t id = ray_sym_intern(data + start, (size_t)str_len);
      if (id < 0) {
        ray_release(ray_obj);
        PyBuffer_Release(&offsets_buffer_view);
        PyBuffer_Release(&data_buffer_view);
        if (null_bitmap_py != NULL)
          Py_DECREF(null_bitmap_py);
        PyErr_SetString(PyExc_RuntimeError,
                        "Failed to intern symbol from arrow data");
        return NULL;
      }
      ids[i] = id;
    }
    ray_obj->len = length;

    PyBuffer_Release(&offsets_buffer_view);
    PyBuffer_Release(&data_buffer_view);
    if (null_bitmap_py != NULL)
      Py_DECREF(null_bitmap_py);

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

    PyObject *null_bitmap_py = PySequence_GetItem(buffers, 0);
    PyObject *offsets_buffer_py = PySequence_GetItem(buffers, 1);
    PyObject *data_buffer_py = PySequence_GetItem(buffers, 2);
    Py_DECREF(buffers);

    if (offsets_buffer_py == NULL || data_buffer_py == NULL) {
      if (null_bitmap_py != NULL)
        Py_DECREF(null_bitmap_py);
      if (offsets_buffer_py != NULL)
        Py_DECREF(offsets_buffer_py);
      if (data_buffer_py != NULL)
        Py_DECREF(data_buffer_py);
      return NULL;
    }

    Py_buffer offsets_buffer_view;
    if (PyObject_GetBuffer(offsets_buffer_py, &offsets_buffer_view,
                           PyBUF_SIMPLE) < 0) {
      Py_DECREF(offsets_buffer_py);
      Py_DECREF(data_buffer_py);
      if (null_bitmap_py != NULL)
        Py_DECREF(null_bitmap_py);
      return NULL;
    }
    Py_DECREF(offsets_buffer_py);

    Py_buffer data_buffer_view;
    if (PyObject_GetBuffer(data_buffer_py, &data_buffer_view, PyBUF_SIMPLE) <
        0) {
      PyBuffer_Release(&offsets_buffer_view);
      Py_DECREF(data_buffer_py);
      if (null_bitmap_py != NULL)
        Py_DECREF(null_bitmap_py);
      return NULL;
    }
    Py_DECREF(data_buffer_py);

    const int32_t *offsets = (const int32_t *)offsets_buffer_view.buf;
    const char *data = (const char *)data_buffer_view.buf;

    obj_p ray_obj = ray_vec_new(RAY_STR, (int64_t)length);
    if (ray_obj == NULL || RAY_IS_ERR(ray_obj)) {
      if (ray_obj)
        ray_release(ray_obj);
      PyBuffer_Release(&offsets_buffer_view);
      PyBuffer_Release(&data_buffer_view);
      if (null_bitmap_py != NULL)
        Py_DECREF(null_bitmap_py);
      PyErr_SetString(PyExc_RuntimeError, "Failed to create string vector");
      return NULL;
    }

    for (Py_ssize_t i = 0; i < length; i++) {
      int32_t str_len = offsets[i + 1] - offsets[i];
      ray_obj = ray_str_vec_append(ray_obj, data + offsets[i], (size_t)str_len);
      if (ray_obj == NULL || RAY_IS_ERR(ray_obj)) {
        if (ray_obj)
          ray_release(ray_obj);
        PyBuffer_Release(&offsets_buffer_view);
        PyBuffer_Release(&data_buffer_view);
        if (null_bitmap_py != NULL)
          Py_DECREF(null_bitmap_py);
        PyErr_SetString(PyExc_RuntimeError, "Failed to append string");
        return NULL;
      }
    }

    PyBuffer_Release(&offsets_buffer_view);
    PyBuffer_Release(&data_buffer_view);
    if (null_bitmap_py != NULL)
      Py_DECREF(null_bitmap_py);

    return raypy_wrap_ray_object(ray_obj);
  }

  PyObject *null_bitmap_py = PySequence_GetItem(buffers, 0);
  PyObject *data_buffer_py = PySequence_GetItem(buffers, 1);
  Py_DECREF(buffers);

  if (data_buffer_py == NULL) {
    if (null_bitmap_py != NULL)
      Py_DECREF(null_bitmap_py);
    return NULL;
  }

  Py_ssize_t length = PyObject_Length(arrow_array_obj);
  if (length < 0) {
    Py_DECREF(data_buffer_py);
    if (null_bitmap_py != NULL)
      Py_DECREF(null_bitmap_py);
    return NULL;
  }

  Py_buffer data_buffer_view;
  if (PyObject_GetBuffer(data_buffer_py, &data_buffer_view, PyBUF_SIMPLE) < 0) {
    Py_DECREF(data_buffer_py);
    if (null_bitmap_py != NULL)
      Py_DECREF(null_bitmap_py);
    return NULL;
  }
  Py_DECREF(data_buffer_py);

  Py_buffer null_bitmap_view = {0};
  int has_nulls = (null_bitmap_py != NULL && null_bitmap_py != Py_None);
  if (has_nulls) {
    if (PyObject_GetBuffer(null_bitmap_py, &null_bitmap_view, PyBUF_SIMPLE) <
        0) {
      PyBuffer_Release(&data_buffer_view);
      Py_DECREF(null_bitmap_py);
      return NULL;
    }
    Py_DECREF(null_bitmap_py);
  }

  size_t element_size = scalar_elem_size(vector_type_code);
  if (element_size == 0 || vector_type_code == RAY_GUID) {
    PyBuffer_Release(&data_buffer_view);
    if (has_nulls)
      PyBuffer_Release(&null_bitmap_view);
    PyErr_SetString(PyExc_ValueError,
                    "Unsupported type code for Arrow array conversion");
    return NULL;
  }

  int is_boolean_bitmap = (vector_type_code == RAY_BOOL);
  size_t expected_size;

  if (is_boolean_bitmap) {
    expected_size = ((size_t)length + 7) / 8;
  } else {
    expected_size = (size_t)length * element_size;
  }

  if ((size_t)data_buffer_view.len < expected_size) {
    PyBuffer_Release(&data_buffer_view);
    if (has_nulls)
      PyBuffer_Release(&null_bitmap_view);
    PyErr_SetString(PyExc_ValueError, "Arrow data buffer too small");
    return NULL;
  }

  obj_p ray_obj = ray_vec_new((int8_t)vector_type_code, (int64_t)length);
  if (ray_obj == NULL || RAY_IS_ERR(ray_obj)) {
    if (ray_obj)
      ray_release(ray_obj);
    PyBuffer_Release(&data_buffer_view);
    if (has_nulls)
      PyBuffer_Release(&null_bitmap_view);
    PyErr_SetString(PyExc_RuntimeError, "Failed to create vector");
    return NULL;
  }

  if (is_boolean_bitmap) {
    const unsigned char *bitmap = (const unsigned char *)data_buffer_view.buf;
    unsigned char *bytes = (unsigned char *)ray_data(ray_obj);
    for (Py_ssize_t i = 0; i < length; i++) {
      size_t byte_idx = (size_t)i / 8;
      size_t bit_idx = (size_t)i % 8;
      bytes[i] = (bitmap[byte_idx] >> bit_idx) & 1u;
    }
  } else {
    memcpy(ray_data(ray_obj), data_buffer_view.buf, expected_size);
  }
  ray_obj->len = length;

  PyBuffer_Release(&data_buffer_view);
  if (has_nulls)
    PyBuffer_Release(&null_bitmap_view);

  return raypy_wrap_ray_object(ray_obj);
}
