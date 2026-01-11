#include "rayforce_c.h"

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

  size_t element_size;
  int vector_type_code = type_code < 0 ? -type_code : type_code;

  switch (vector_type_code) {
  case TYPE_I16:
    element_size = 2; // sizeof(int16_t)
    break;
  case TYPE_I32:
    element_size = 4; // sizeof(int32_t)
    break;
  case TYPE_I64:
    element_size = 8; // sizeof(int64_t)
    break;
  case TYPE_F64:
    element_size = 8; // sizeof(double)
    break;
  case TYPE_B8:
    element_size = 1; // sizeof(uint8_t)
    break;
  case TYPE_U8:
    element_size = 1; // sizeof(uint8_t)
    break;
  default:
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

  obj_p ray_obj = vector(vector_type_code, (u64_t)length);
  if (ray_obj == NULL) {
    PyBuffer_Release(&buffer_view);
    PyErr_SetString(PyExc_RuntimeError, "Failed to create vector");
    return NULL;
  }

  const void *src_data = buffer_view.buf;
  int has_nulls = (null_bitmap_obj != NULL && null_bitmap_obj != Py_None);

  Py_buffer null_bitmap_view = {0};
  if (has_nulls) {
    if (PyObject_GetBuffer(null_bitmap_obj, &null_bitmap_view, PyBUF_SIMPLE) <
        0) {
      drop_obj(ray_obj);
      PyBuffer_Release(&buffer_view);
      return NULL;
    }
    size_t min_bitmap_size = ((size_t)length + 7) / 8;
    if ((size_t)null_bitmap_view.len < min_bitmap_size) {
      drop_obj(ray_obj);
      PyBuffer_Release(&null_bitmap_view);
      PyBuffer_Release(&buffer_view);
      PyErr_SetString(PyExc_ValueError, "Null bitmap too small");
      return NULL;
    }
  }

  for (Py_ssize_t i = 0; i < length; i++) {
    obj_p item = NULL;

    // Check null bitmap if provided
    if (has_nulls) {
      size_t byte_idx = (size_t)i / 8;
      size_t bit_idx = (size_t)i % 8;
      const unsigned char *bitmap_bytes =
          (const unsigned char *)null_bitmap_view.buf;
      if (!(bitmap_bytes[byte_idx] & (1 << bit_idx))) {
        continue;
      }
    }

    switch (vector_type_code) {
    case TYPE_I16: {
      const short *data = (const short *)src_data;
      item = i16(data[i]);
      break;
    }
    case TYPE_I32: {
      const int *data = (const int *)src_data;
      item = i32(data[i]);
      break;
    }
    case TYPE_I64: {
      const long long *data = (const long long *)src_data;
      item = i64(data[i]);
      break;
    }
    case TYPE_F64: {
      const double *data = (const double *)src_data;
      item = f64(data[i]);
      break;
    }
    case TYPE_B8: {
      const unsigned char *data = (const unsigned char *)src_data;
      item = b8(data[i] ? 1 : 0);
      break;
    }
    case TYPE_U8: {
      const unsigned char *data = (const unsigned char *)src_data;
      item = u8(data[i]);
      break;
    }
    default:
      drop_obj(ray_obj);
      if (has_nulls)
        PyBuffer_Release(&null_bitmap_view);
      PyBuffer_Release(&buffer_view);
      PyErr_SetString(PyExc_ValueError, "Unsupported type code");
      return NULL;
    }

    if (item == NULL) {
      drop_obj(ray_obj);
      if (has_nulls)
        PyBuffer_Release(&null_bitmap_view);
      PyBuffer_Release(&buffer_view);
      PyErr_SetString(PyExc_RuntimeError, "Failed to create element");
      return NULL;
    }

    if (ins_obj(&ray_obj, (i64_t)i, item) == NULL) {
      drop_obj(item);
      drop_obj(ray_obj);
      if (has_nulls)
        PyBuffer_Release(&null_bitmap_view);
      PyBuffer_Release(&buffer_view);
      PyErr_SetString(PyExc_RuntimeError, "Failed to insert element");
      return NULL;
    }
  }

  PyBuffer_Release(&buffer_view);
  if (has_nulls) {
    PyBuffer_Release(&null_bitmap_view);
  }

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

  if (vector_type_code == TYPE_SYMBOL) {
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

    obj_p ray_obj = vector(TYPE_SYMBOL, (u64_t)length);

    if (ray_obj == NULL) {
      PyBuffer_Release(&offsets_buffer_view);
      PyBuffer_Release(&data_buffer_view);
      if (null_bitmap_py != NULL)
        Py_DECREF(null_bitmap_py);
      PyErr_SetString(PyExc_RuntimeError, "Failed to create vector");
      return NULL;
    }

    for (Py_ssize_t i = 0; i < length; i++) {
      int32_t start = offsets[i];
      int32_t end = offsets[i + 1];
      int32_t str_len = end - start;

      obj_p sym = symbol(data + start, (i64_t)str_len);
      if (sym == NULL) {
        drop_obj(ray_obj);
        PyBuffer_Release(&offsets_buffer_view);
        PyBuffer_Release(&data_buffer_view);
        if (null_bitmap_py != NULL)
          Py_DECREF(null_bitmap_py);
        PyErr_SetString(PyExc_RuntimeError,
                        "Limit of 2^24 unique symbols reached.");
        return NULL;
      }

      if (ins_obj(&ray_obj, (i64_t)i, sym) == NULL) {
        drop_obj(sym);
        drop_obj(ray_obj);
        PyBuffer_Release(&offsets_buffer_view);
        PyBuffer_Release(&data_buffer_view);
        if (null_bitmap_py != NULL)
          Py_DECREF(null_bitmap_py);
        PyErr_SetString(PyExc_RuntimeError,
                        "Failed to insert symbol into vector");
        return NULL;
      }
    }

    PyBuffer_Release(&offsets_buffer_view);
    PyBuffer_Release(&data_buffer_view);
    if (null_bitmap_py != NULL)
      Py_DECREF(null_bitmap_py);

    return raypy_wrap_ray_object(ray_obj);
  }

  if (vector_type_code == TYPE_C8) {
    if (num_buffers < 3) {
      Py_DECREF(buffers);
      PyErr_SetString(PyExc_ValueError, "Invalid Arrow string buffer");
      return NULL;
    }

    // Get length first
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

    // Arrow offsets are int32 or int64, but typically int32 for strings
    // offsets has (length + 1) elements: offsets[i] to offsets[i+1] defines
    // string i
    const int32_t *offsets = (const int32_t *)offsets_buffer_view.buf;
    const char *data = (const char *)data_buffer_view.buf;

    obj_p ray_obj = vector(TYPE_LIST, (i64_t)length);

    if (ray_obj == NULL) {
      PyBuffer_Release(&offsets_buffer_view);
      PyBuffer_Release(&data_buffer_view);
      if (null_bitmap_py != NULL)
        Py_DECREF(null_bitmap_py);
      PyErr_SetString(PyExc_RuntimeError, "Failed to create list");
      return NULL;
    }

    // Direct access to list elements via AS_LIST macro
    obj_p *list_ptr = AS_LIST(ray_obj);
    for (Py_ssize_t i = 0; i < length; i++) {
      int32_t str_len = offsets[i + 1] - offsets[i];

      obj_p str_obj = C8((i64_t)str_len);
      if (str_obj == NULL) {
        for (Py_ssize_t j = 0; j < i; j++) {
          drop_obj(list_ptr[j]);
        }
        drop_obj(ray_obj);
        PyBuffer_Release(&offsets_buffer_view);
        PyBuffer_Release(&data_buffer_view);
        if (null_bitmap_py != NULL)
          Py_DECREF(null_bitmap_py);
        PyErr_SetString(PyExc_RuntimeError, "Failed to create string object");
        return NULL;
      }
      memcpy(AS_C8(str_obj), data + offsets[i], str_len);

      // Direct assignment to pre-allocated list
      list_ptr[i] = str_obj;
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

  size_t element_size;
  switch (vector_type_code) {
  case TYPE_I16:
    element_size = 2;
    break;
  case TYPE_I32:
    element_size = 4;
    break;
  case TYPE_I64:
    element_size = 8;
    break;
  case TYPE_F64:
    element_size = 8;
    break;
  case TYPE_B8:
    element_size = 1;
    break;
  case TYPE_U8:
    element_size = 1;
    break;
  case TYPE_TIMESTAMP:
    element_size = 8;
    break;
  default:
    PyBuffer_Release(&data_buffer_view);
    if (has_nulls)
      PyBuffer_Release(&null_bitmap_view);
    PyErr_SetString(PyExc_ValueError,
                    "Unsupported type code for Arrow array conversion");
    return NULL;
  }

  int is_boolean_bitmap = (vector_type_code == TYPE_B8);
  size_t expected_size;

  if (is_boolean_bitmap) {
    expected_size = ((size_t)length + 7) / 8;
  } else {
    expected_size = (size_t)length * element_size;
  }

  if (!is_boolean_bitmap && (size_t)data_buffer_view.len < expected_size) {
    PyBuffer_Release(&data_buffer_view);
    if (has_nulls)
      PyBuffer_Release(&null_bitmap_view);
    PyErr_SetString(PyExc_ValueError, "Arrow data buffer too small");
    return NULL;
  } else if (is_boolean_bitmap &&
             (size_t)data_buffer_view.len < expected_size) {
    PyBuffer_Release(&data_buffer_view);
    if (has_nulls)
      PyBuffer_Release(&null_bitmap_view);
    PyErr_SetString(PyExc_ValueError, "Arrow boolean bitmap too small");
    return NULL;
  }

  obj_p ray_obj = vector(vector_type_code, (u64_t)length);
  if (ray_obj == NULL) {
    PyBuffer_Release(&data_buffer_view);
    if (has_nulls)
      PyBuffer_Release(&null_bitmap_view);
    PyErr_SetString(PyExc_RuntimeError, "Failed to create vector");
    return NULL;
  }

  const void *src_data = data_buffer_view.buf;
  void *dst_data = NULL;

  switch (vector_type_code) {
  case TYPE_I16:
    dst_data = AS_I16(ray_obj);
    break;
  case TYPE_I32:
    dst_data = AS_I32(ray_obj);
    break;
  case TYPE_I64:
    dst_data = AS_I64(ray_obj);
    break;
  case TYPE_F64:
    dst_data = AS_F64(ray_obj);
    break;
  case TYPE_B8:
    dst_data = AS_B8(ray_obj);
    break;
  case TYPE_U8:
    dst_data = AS_U8(ray_obj);
    break;
  case TYPE_TIMESTAMP:
    dst_data = AS_TIMESTAMP(ray_obj);
    break;
  default:
    drop_obj(ray_obj);
    if (has_nulls)
      PyBuffer_Release(&null_bitmap_view);
    PyBuffer_Release(&data_buffer_view);
    PyErr_SetString(PyExc_ValueError, "Unsupported type code for bulk copy");
    return NULL;
  }

  if (is_boolean_bitmap) {
    const unsigned char *bitmap = (const unsigned char *)src_data;
    unsigned char *bytes = (unsigned char *)dst_data;
    for (Py_ssize_t i = 0; i < length; i++) {
      size_t byte_idx = (size_t)i / 8;
      size_t bit_idx = (size_t)i % 8;
      bytes[i] = (bitmap[byte_idx] >> bit_idx) & 1;
    }
  } else {
    memcpy(dst_data, src_data, expected_size);
  }

  PyBuffer_Release(&data_buffer_view);
  if (has_nulls)
    PyBuffer_Release(&null_bitmap_view);

  return raypy_wrap_ray_object(ray_obj);
}
